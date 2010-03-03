function dismissRelatedLookupPopup(win, chosenId) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if ($(elem).hasClass('vAutocompleteWidget')) {
        $("#"+ name +"_raw").val(chosenId);
        $("#"+ name +"_raw").blur();
    } else if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
        elem.value += ',' + chosenId;
    } else {
        document.getElementById(name).value = chosenId;
    }
    win.close();
}
