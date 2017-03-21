var SCROLLABLE_NROWS_THRESHOLD = 5;

$(document).ready(function() {
    /* If the tables are longer than a certain number of lines, then
    add the `scrollable-table` class which adds a scrollbar */
    $('div.scrollable-table-placeholder').each(function() {
        var elem = $(this);
        var tables = elem.children('table');

        if (tables.length != 1) {
            console.error("unknown number of tables found");
            return;
        }

        var table = tables[0];
        var rows = $(table).find('tr');

        if (rows.length > SCROLLABLE_NROWS_THRESHOLD) {
            elem.addClass('scrollable-table');
        }
    });
});
