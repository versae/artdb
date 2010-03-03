(function() {

BaseDynamicFormSetClass = function() {};
BaseDynamicFormSetClass.prototype.getElementsByIdStartsWith = function(root, inPrefix){
    var elemArray = new Array;
    if (typeof root.firstChild != 'undefined') {
        var elem = root.firstChild;
        var reg = new RegExp ('^'+ inPrefix +'.*');
        while (elem != null) {
            if (typeof elem.firstChild != 'undefined') {
                elemArray = elemArray.concat(BaseDynamicFormSetClass.prototype.getElementsByIdStartsWith(elem, inPrefix));
            }
            if (typeof elem.id != 'undefined') {
                if (elem.id.match(reg)) {
                    elemArray.push(elem);
                }
            }
            elem = elem.nextSibling;
        }
    }
    return elemArray;
}
BaseDynamicFormSetClass.prototype.hideTag = function(tag) {
        if ((tag.parentNode.nodeName == 'P') || (tag.parentNode.nodeName == 'LI')
        || (tag.parentNode.nodeName == 'DIV')) {
            tag.parentNode.style.display = 'none';
        } else if (tag.parentNode.nodeName == 'TD') {
            tag.parentNode.parentNode.style.display = 'none';
        } else {
            tag.style.display = 'none';
        }
}
BaseDynamicFormSetClass.prototype.markAsDeleted = function(formSetId, DELETION_FIELD_NAME) {
    var checkboxInput = document.getElementById(formSetId + DELETION_FIELD_NAME);
    if (checkboxInput.checked) {
        var formSetFields = BaseDynamicFormSetClass.prototype.getElementsByIdStartsWith(document, formSetId);
        for (var i=0; i<formSetFields.length; i++) {
            var field = formSetFields[i];
            BaseDynamicFormSetClass.prototype.hideTag(field);
        }
        var formSetLabels = document.getElementsByTagName("LABEL");
        var reg = new RegExp ('^'+ formSetId +'.*');
        for (var i=0; i<formSetLabels.length; i++) {
            var label = formSetLabels[i];
            var labelFor = label.getAttribute('FOR');
            if (labelFor.match(reg)) {
                BaseDynamicFormSetClass.prototype.hideTag(label);
            }
        }
    }
}
BaseDynamicFormSetClass.prototype.addOther = function(formSetId, hash, BLANK_FORM, INITIAL_FORM_COUNT, TOTAL_FORM_COUNT, moreJSCommands) {
    var as_method = BaseDynamicFormSetClass.prototype.asMethod[hash] || "as_table";
    var blankForm = document.getElementById(formSetId +"-"+ BLANK_FORM +"-"+as_method);
    var initialForm = document.getElementById(formSetId +"-"+ INITIAL_FORM_COUNT);
    var totalForm = document.getElementById(formSetId +"-"+ TOTAL_FORM_COUNT);
    var formString = eval('('+ blankForm.value +')')
    var form = formString.split(BLANK_FORM).join(totalForm.value);
    var insertionPoint = document.getElementById(hash);
    if (RegExp("MSIE|Safari").test(navigator.userAgent) || navigator.product != "Gecko") {
        var insertionPointOuterHTML = insertionPoint.outerHTML;
        insertionPoint.outerHTML = form + insertionPointOuterHTML;
    } else if (RegExp("Opera").test(navigator.userAgent) || navigator.product != "Gecko") {
        var insertionPointOuterHTML = insertionPoint.cloneNode(false).outerHTML;
        insertionPoint.cloneNode(false).outerHTML = form + insertionPointOuterHTML;
    } else {
        var insertionPointOuterHTML = BaseDynamicFormSetClass.prototype.getOuterHTML(insertionPoint);
        BaseDynamicFormSetClass.prototype.setOuterHTML(insertionPoint, form + insertionPointOuterHTML);
    }
    totalForm.value = parseInt(totalForm.value) + 1;
    if (moreJSCommands) {
        eval(moreJSCommands);
    }
    
}
/*
Code for outerHTML from http://webfx.eae.net/dhtml/ieemu/ieemu.js
*/
BaseDynamicFormSetClass.prototype.setOuterHTML = function(root, sHTML) {
    var r = root.ownerDocument.createRange();
    r.setStartBefore(root);
    var df = r.createContextualFragment(sHTML);
    root.parentNode.replaceChild(df, root);
}
BaseDynamicFormSetClass.prototype.canHaveChildren = function(root) {
    switch (root.tagName) {
        case "AREA":
        case "BASE":
        case "BASEFONT":
        case "COL":
        case "FRAME":
        case "HR":
        case "IMG":
        case "BR":
        case "INPUT":
        case "ISINDEX":
        case "LINK":
        case "META":
        case "PARAM":
        return false;
    }
    return true;
}
BaseDynamicFormSetClass.prototype.getOuterHTML = function(root) {
    var attr, attrs = root.attributes;
    var str = "<" + root.tagName;
    for (var i = 0; i < attrs.length; i++) {
        attr = attrs[i];
        if (attr.specified)
            str += " " + attr.name + '="' + attr.value + '"';
    }
    if (!BaseDynamicFormSetClass.prototype.canHaveChildren(root))
        return str + ">";
    return str + ">" + root.innerHTML + "</" + root.tagName + ">";
}
BaseDynamicFormSetClass.prototype.asMethod = {};
BaseDynamicFormSet = new BaseDynamicFormSetClass();

})();
