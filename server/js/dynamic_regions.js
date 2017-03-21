/* Function to add a click handler to images where regions have been defined. This
 * allows the image to be scaled, either by the browser zoom function, or when the page
 * is scaled through the use of bootstrap.
 */
function add_clickable_handler(elem) {
    var elem = $(elem);

    var regions_url = elem.data('region-definition');
    var region_definition = $.getJSON(regions_url, {}, function(data, st, xhr) {
        $(elem).click(function(e) {
            e.preventDefault();
            var target = e.target;
            var height_scaling = target.naturalHeight / target.height;
            var width_scaling = target.naturalWidth / target.width;

            var posX = e.pageX - $(this).offset().left;
            var posY = e.pageY - $(this).offset().top;

            var scaledX = posX * width_scaling;
            var scaledY = posY * height_scaling;

            for (var i=0; i<data.length; i++) {
                if ((scaledX >= data[i].xmin) && (scaledX < data[i].xmax)) {
                    if ((scaledY >= data[i].ymin) && (scaledY < data[i].ymax)) {
                        window.location = data[i].href;
                        return;
                    }
                }
            }
        });
    });
}

/* Actually attach the event handlers to any images defined with
 * the `region-plot` class.
 */
$(document).ready(function() {
    $('img.region-plot').map(function(i, elem) { add_clickable_handler(elem); });
});
