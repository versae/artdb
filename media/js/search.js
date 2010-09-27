var Artwork_fields = {
    'Title': 'title',
    'Creation year start': 'creation_year_start',
    'Creation year end': 'creation_year_end',
    'Original place': 'original_place__title',
    'Current place': 'current_place__title',
    'Serie': 'serie__title',
    'Creators': 'creators__name'
};
var Creator_fields = {
    'Name': 'name',
    'Birth year': 'birth_year',
    'Birth place': 'birth_place__title',
    'Death year': 'death_year',
    'Death place': 'death_place__title',
    'Masters': 'masters__name'
};
var Serie_fields = {
    'Title': 'title'
};

var urlParams = {};

this.selectionChanged = function(field_index){
    $('.pv_search_select').change(function(){
        object_name = $(".pv_search_select option:selected");
        
        for (var i = 1; i < 4; i++) {
            $('#field' + i).get(0).options.length = 0;
            $('#field' + i).get(0).options[0] = new Option("Select field", "-1");
            if (object_name.val() != "") {
                $.each(eval(object_name.val() + '_fields'), function(key, value){
                    $('#field' + i).get(0).options[$('#field' + i).get(0).options.length] = new Option(key, value);
                });
            }
            $('#field' + i).trigger('change');
        }
    });
    
};

this.fieldsChanged = function(field_index){
    $('#field' + field_index).change(function(){
        field_value = $('#field' + field_index + " option:selected");
        if (field_value.val() != "-1") {
            if ($('#text' + field_index).attr("disabled")) {
                $("#text" + field_index).removeAttr("disabled");
            }
        }
        else {
            if (!($('#text' + field_index).attr("disabled"))) {
                $("#text" + field_index).val("");
                $("#text" + field_index).attr("disabled", true);
            }
        }
    });
};

this.onSearchClicked = function(){
    $('.search_fields_button').click(function(){
        var queryparams = new Array();
        var queryVals = new Array();
        var operators = new Array();
        object_name = $(".pv_search_select option:selected");
        object_name = object_name.val();
        if (object_name != "") {
            for (var i = 1; i < 4; i++) {
                textVal = $('#text' + i).val();
                if (textVal != '') {
                    queryVals.push(textVal);
                    queryparams.push($('#field' + i + " option:selected").val());
                }
            }
        }
        for (var i = 1; i < 3; i++) {
            opVal = $('#op' + i + " option:selected").val()
            if (opVal != '') {
                operators.push(opVal);
            }
        }
        
        callAjax(object_name, queryparams, queryVals, operators);
        
    });
};

this.initialize_dropdowns = function(){
    $(".pv_search_select option[value='']").attr('selected', 'selected');
    $('.pv_search_select').trigger('change');
    $("#op1 option")[0]['selected'] = true;
    $("#op2 option")[0]['selected'] = true;
}

// starting the script on page load
$(document).ready(function(){
    selectionChanged();
    for (var i = 1; i < 4; i++) {
        fieldsChanged(i);
        $("#text" + i).val("");
        $('#text' + i).attr("disabled", true);
    }
    onSearchClicked();
    loadTable();
    initialize_dropdowns();
});
