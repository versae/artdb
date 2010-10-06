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

this.selectionChanged = function(){
    $('.pv_search_select').change(function(){
        object_name = $(".pv_search_select option:selected");
        object_name = object_name.val();
        
		$('#search_table_div').html("");
        $('#criteria_table').html("<tbody></tbody>");
        
        if (object_name != "") {
            $('#type_selection').val(object_name);
            addCriteria(1);
        }else{
			$('#type_selection').val("");
		}
    });
    
};

this.fillOperators = function(index){
    $('#op' + index).get(0).options[$('#op' + index).get(0).options.length] = new Option("and/or", "or");
    $('#op' + index).get(0).options[$('#op' + index).get(0).options.length] = new Option("and", "and");
    $('#op' + index).get(0).options[$('#op' + index).get(0).options.length] = new Option("or", "or");
}

this.addCriteria = function(index){

    if (index == 1) {
        $('#criteria_table > tbody:last').append('<tr><td width="25%"></td><td width="25%" class="td_height"><input type="text" id="text1" class="text_search" /></td><td width="25%" align="left" class="td_height"><select id="field1" class="search_select"></select></td><td width="25%" align="left"><div><input type="button" class="select_more" id="more1" /><span id="error1" class="criteria_span">Please fill the criteria.</span></div></td></tr>');
    }
    else {
        $('#criteria_table > tbody:last').append('<tr><td width="25%" align="right"><select id="op' + index + '" class="search_select" style="width:70px;"></select></td><td width="25%" class="td_height"><input type="text" id="text' + index + '" class="text_search" /></td><td width="25%" align="left" class="td_height"><select id="field' + index + '" class="search_select"></select></td><td width="25%" align="left"><div><input type="button" class="select_more" id="more' + index + '" /><span id="error' + index + '" class="criteria_span">Please fill the criteria.</span></div></td></tr>');
        fillOperators(index);
    }
    
    var selection = $('#type_selection').val();
    $('#field' + index).get(0).options[$('#field' + index).get(0).options.length] = new Option("Choose..", -1);
    
    $.each(eval(selection + '_fields'), function(key, value){
        $('#field' + index).get(0).options[$('#field' + index).get(0).options.length] = new Option(key, value);
    });
    
    fieldsChanged(index);
    $("#text" + index).val("");
    $('#text' + index).attr("disabled", true);
    $('#error' + index).hide();
    addNewRow(index);
    
}

this.addNewRow = function(index){

    $('#more' + index).click(function(){
        var newIndex = index + 1;
        
        if ($("#text" + index).val() != "") {
            $('#error' + index).hide();
            addCriteria(newIndex);
        }
        else {
            $('#error' + index).show();
        }
    })
    
}

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
        
        object_name = $("#type_selection").val();
		
        if (object_name != "") {
        
            var i = 1;
            
            while ($("#text" + i).length != 0) {
            
                textVal = $('#text' + i).val();
                if (textVal != '') {
                    queryVals.push(textVal);
                    queryparams.push($('#field' + i + " option:selected").val());
                    if ($("#op" + i).length != 0) 
                        operators.push($('#op' + i + " option:selected").val());
                }
                $('#error' + i).hide();
                i = i + 1;
            }
			
			callAjax(object_name, queryparams, queryVals, operators);
        }
        
    });
};

this.initialize_dropdowns = function(){
    $(".pv_search_select option[value='']").attr('selected', 'selected');
    $('.pv_search_select').trigger('change');
}

this.loadTable = function(){
    var e, d = function(s){
        return decodeURIComponent(s.replace(/\+/g, " "));
    }, q = window.location.search.substring(1), r = /([^&=]+)=?([^&]*)/g;
    
    while (e = r.exec(q)) 
        urlParams[d(e[1])] = d(e[2]);
	
    if (urlParams.data) {
        data = urlParams.data;
        $.get($('#search_url').val(), {
            data: data
        }, function(result){
            $('#search_table_div').html(result);
        });
    }
};

this.callAjax = function(object_name, queryparams, queryVals, operators){
    $.ajax({
        url: $('#search_url').val(),
        data: {
            objectType: object_name,
            params: queryparams,
            vals: queryVals,
            ops: operators
        },
        traditional: true,
        success: function(result){
            $('#search_table_div').html(result);
        }
    });
}
// starting the script on page load
$(document).ready(function(){
    selectionChanged();
    onSearchClicked();
    loadTable();
    initialize_dropdowns();
});
