$(document).ready(function() {
    $('img.region-plot').map(function(i, elem) { add_clickable_handler(elem); });
});

function add_clickable_handler(elem) {
    var elem = $(elem);
    console.log('Adding event handler to ' + elem);

    var regions_url = elem.data('region-definition');
    var region_definition = $.getJSON(regions_url, {}, function(data, st, xhr) {
        $(elem).click(function(e) {
            var target = e.target;
            var height_scaling = target.naturalHeight / target.height;
            var width_scaling = target.naturalWidth / target.width;

            var posX = e.pageX - $(this).offset().left;
            var posY = e.pageY - $(this).offset().top;

            var scaledX = posX * width_scaling;
            var scaledY = posY * height_scaling;

            console.log(data);
        });
    });
}
