interface Region {
    xmin: number;
    xmax: number;
    ymin: number;
    ymax: number;
    href: string;
}

interface MousePos {
    x: number;
    y: number;
}

interface Scaling {
    x: number;
    y: number;
}

class Bound {
    xmin: number;
    xmax: number;
    ymin: number;
    ymax: number;

    constructor(xmin: number, xmax: number, ymin: number, ymax: number) {
        this.xmin = xmin;
        this.xmax = xmax;
        this.ymin = ymin;
        this.ymax = ymax;
    }

    contains(e: MousePos): boolean {
        return ((e.x >= this.xmin) &&
            (e.x <= this.xmax) &&
            (e.y >= this.ymin) &&
            (e.y <= this.ymax));
    }
}

class RegionHandler {
    canvas: HTMLCanvasElement;
    ctx: CanvasRenderingContext2D | null;
    image: HTMLImageElement;

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');
        if (this.ctx === null) {
            console.error("2d rendering context not supported :(");
        }
    }

    public add_mouse_handlers(image_url: string, regions_url: string) {
        let self = this;
        self.image = new Image();
        self.image.src = image_url;
        self.image.onload = function(event) {
            self.canvas.width = self.image.naturalWidth;
            self.canvas.height = self.image.naturalHeight;
            self.reset_canvas();

            $.getJSON(regions_url, function(regions: Array<Region>) {
                self.add_handlers(regions);
            }).fail(function() {
                self.show_error("Regions not found. Interactivity disabled");
                console.error(`Cannot fetch regions url: ${regions_url}`);
            });
        };

        self.image.onerror = function(e: ErrorEvent) {
            console.error(`Cannot load image: ${image_url}`);
        };
    }

    add_handlers(regions: Array<Region>) {
        let self = this;

        let bounds: Bound = self.compute_bounds(regions);

        self.canvas.addEventListener('mousemove', function(e: MouseEvent) {
            self.reset_canvas();

            let click = self.scaled_click(e);

            if (!bounds.contains(click)) {
                return;
            }

            let region: Region | null = self.region_for_event(regions, click);

            if (region != null) {
                self.add_region(region);
            }
        });

        self.canvas.addEventListener('click', function(e: MouseEvent) {
            self.reset_canvas();

            let click = self.scaled_click(e);

            if (!bounds.contains(click)) {
                return;
            }

            let region: Region | null = self.region_for_event(regions, click);

            if (region != null) {
                console.log('Changing window url to ' + region.href);
            }
        });

        self.canvas.addEventListener('mouseleave', function(e: MouseEvent) {
            self.reset_canvas();
        });
    }

    scaled_click(e: MouseEvent): MousePos {
        let scaling: Scaling = {
            x: this.canvas.width / this.canvas.clientWidth,
            y: this.canvas.height / this.canvas.clientHeight,
        };

        let click: MousePos = {
            x: e.offsetX * scaling.x,
            y: e.offsetY * scaling.y,
        };

        return click;
    }

    compute_bounds(regions: Array<Region>): Bound {
        var xmin = Infinity;
        var xmax = -Infinity;
        var ymin = Infinity;
        var ymax = -Infinity;

        for (let region of regions) {
            if (region.xmin < xmin) xmin = region.xmin;
            if (region.xmax > xmax) xmax = region.xmax;
            if (region.ymin < ymin) ymin = region.ymin;
            if (region.ymax > ymax) ymax = region.ymax;
        }

        return new Bound(xmin, xmax, ymin, ymax);
    }

    region_for_event(regions: Array<Region>, e: MousePos): Region | null {

        let n_regions = regions.length;
        let x = e.x;
        let y = e.y;

        for (let r of regions) {
            if ((x >= r.xmin) && (x < r.xmax) && (y >= r.ymin) && (y < r.ymax)) {
                return r;
            }
        }

        return null;
    }

    add_region(region: Region) {
        let self = this;

        self.reset_canvas();

        let dx = region.xmax - region.xmin;
        let dy = region.ymax - region.ymin;

        self.context().strokeStyle = '#97CBD1';
        self.context().strokeRect(region.xmin, region.ymin, dx, dy);
    }

    context(): CanvasRenderingContext2D {
        return this.ctx!;
    }

    reset_canvas() {
        this.context().clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.context().drawImage(this.image, 0, 0);
    }

    show_error(text: string) {
        this.context().textAlign = 'center';
        this.context().font = '16px serif';

        this.reset_canvas();
        this.context().fillStyle = 'red';
        this.context().fillText(text, this.canvas.width / 2, 0.1 * this.canvas.height);
    }
}
