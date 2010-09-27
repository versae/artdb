google.load('jquery', '1.4.2');


function initialize() {
    var filersToggleSpan = $("#exhibitFiltersToggle");
    var yearFromSelect = $("#exhibitYearFrom");
    var yearToSelect = $("#exhibitYearTo");
    filersToggleSpan.click(function() {
        $("#exhibitFiltersContainer").toggle();
    });

    $("#exhibitYearFrom,#exhibitYearTo").change(function() {
        var updateSpan = $("#exhibitUpdate");
        var outOfRangeSpan = $("#exhibitOutOfRange");
        updateSpan.hide();
        outOfRangeSpan.hide();
        difference = Math.abs(parseInt(yearFromSelect.val()) - parseInt(yearToSelect.val()))
        if (difference > 25) {
            outOfRangeSpan.show();
        } else {
            updateSpan.show();
        }
        $("#exhibitMapLink").attr("href", $("#exhibitMapHidden").val() + "?from="+ yearFromSelect.val() +"&to="+ yearToSelect.val());
    });

    $("#exhibitUpdateRange").click(function() {
        location.search = "?from="+ yearFromSelect.val() +"&to="+ yearToSelect.val();
        return false;
    });
}
google.setOnLoadCallback(initialize);
