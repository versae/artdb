function TimeControl(opts) {
    this.onStart = this.timeStartHandler(opts.onStart || function() {});
    this.onTimeChange = this.timeChangeHandler(opts.onTimeChange || function() {});
    this.onTimeMove = this.timeMoveHandler(opts.onTimeMove || function() {});
    this.onStartChange = this.startChangeHandler(opts.onStartChange || function() {});
    this.onEndChange = this.endChangeHandler(opts.onEndChange || function() {});
    this.css = opts.css || "slider";
    this.id = opts.id || "sliderTimeControl";
    this.start = opts.start || new Date(1900, 1, 1);
    this.end = opts.end || new Date(2100, 1, 1);
    this.yearStart = (opts.start && opts.start.getUTCFullYear()) || 1900;
    this.yearEnd = (opts.end && opts.end.getUTCFullYear()) || 2100;
    this.range = (opts.selected.length == 2);
    this.dateFormat = opts.format || "yy-mm-dd";
    this.min = 0;
    this.max = Math.abs(this.yearEnd - this.yearStart);
    var start = parseInt((this.max+this.min) / 2);
    if (this.range) {
        this.selected = [
            opts.selected[0].getUTCFullYear() - this.yearStart || start,
            opts.selected[1].getUTCFullYear() - this.yearStart || start
        ];
    } else {
        this.selected = opts.selected.getUTCFullYear() - this.yearStart || start;
    }
    this.step = opts.zoom || this.YEAR;
    this.defaultPosition = opts.position || new google.maps.ControlPosition(google.maps.ANCHOR_TOP_LEFT,
                                                                            new google.maps.Size(75, 24));
}
TimeControl.prototype = new google.maps.Control();
TimeControl.prototype.initialize = function(map) {
    var parent = this;
    var container = document.createElement("div");
    $(container).attr("id", this.id);
    var minusButton = document.createElement("div");
    $(minusButton).addClass(this.css +"MinusButton");
    $(minusButton).click(function() {
        $('#'+ parent.id +'MinusDatePicker').datepicker('enable');
        $('#'+ parent.id +'MinusDatePicker').datepicker('show');
    });
    var plusButton = document.createElement("div");
    $(plusButton).addClass(this.css +"PlusButton");
    $(plusButton).click(function() {
        $('#'+ parent.id +'PlusDatePicker').datepicker('enable');
        $('#'+ parent.id +'PlusDatePicker').datepicker('show');
    });
    var timeSlider = document.createElement("div");
    $(timeSlider).addClass(this.css);
    var sliderParams = {
        min: this.min,
        max: this.max,
        step: this.step, 
        range: this.range,
        change: this.onTimeChange,
        slide: this.onTimeMove,
        animate: true
    }
    sliderParams[(this.range) ? 'values' : 'value'] = this.selected;
    var datePickerParams = {
        showButtonPanel: true,
        changeMonth: true,
        changeYear: true,
        yearRange: this.yearStart +':'+ this.yearEnd,
        minDate: this.start,
        maxDate: this.end,
        dateFormat: this.dateFormat
    };

    var minusDatePicker = document.createElement("input");
    $(minusDatePicker).addClass(this.css +"MinusDate");
    $(minusDatePicker).attr('type', 'text');
    $(minusDatePicker).attr('readonly', true);
    $(minusDatePicker).attr('id', this.id +'MinusDatePicker');
    $(minusDatePicker).val($.datepicker.formatDate(this.dateFormat, this.start));

    var minusDatePickerLeft = document.createElement("span");
    $(minusDatePickerLeft).addClass(this.css +"MinusDateLeft");
    var minusDatePickerRight = document.createElement("span");
    $(minusDatePickerRight).addClass(this.css +"MinusDateRight");
    var minusDatePickerContainer = document.createElement("span");
    $(minusDatePickerContainer).addClass(this.css +"MinusDateContainer");
    $(minusDatePickerContainer).attr('id', this.id +'MinusDateContainer');
    $(minusDatePickerContainer).append(minusDatePickerLeft);
    $(minusDatePickerContainer).append(minusDatePicker);
    $(minusDatePickerContainer).append(minusDatePickerRight);

    var plusDatePicker = document.createElement("input");
    $(plusDatePicker).addClass(this.css +"PlusDate");
    $(plusDatePicker).attr('type', 'text');
    $(plusDatePicker).attr('readonly', true);
    $(plusDatePicker).attr('id', this.id +'PlusDatePicker');
    $(plusDatePicker).val($.datepicker.formatDate(this.dateFormat, this.end));

    var plusDatePickerLeft = document.createElement("span");
    $(plusDatePickerLeft).addClass(this.css +"PlusDateLeft");
    var plusDatePickerRight = document.createElement("span");
    $(plusDatePickerRight).addClass(this.css +"PlusDateRight");
    var plusDatePickerContainer = document.createElement("span");
    $(plusDatePickerContainer).addClass(this.css +"PlusDateContainer");
    $(plusDatePickerContainer).attr('id', this.id +'PlusDateContainer');
    $(plusDatePickerContainer).append(plusDatePickerLeft);
    $(plusDatePickerContainer).append(plusDatePicker);
    $(plusDatePickerContainer).append(plusDatePickerRight);

    var selectedInfo = document.createElement("span");
    $(selectedInfo).addClass(this.css +"Selected");
    $(selectedInfo).attr('id', this.id +'SelectedDate');

    var selectedInfoLeft = document.createElement("span");
    $(selectedInfoLeft).addClass(this.css +"SelectedLeft");
    $(selectedInfoLeft).attr('id', this.id +'SelectedLeftDate');

    var selectedInfoRight = document.createElement("span");
    $(selectedInfoRight).addClass(this.css +"SelectedRight");
    $(selectedInfoRight).attr('id', this.id +'SelectedRightDate');

    var selectedContainer = document.createElement("div");
    $(selectedContainer).addClass(this.css +"SelectedContainer");
    $(selectedContainer).attr('id', this.id +'SelectedContainerDate');

    selectedContainer.appendChild(selectedInfoLeft);
    selectedContainer.appendChild(selectedInfo);
    selectedContainer.appendChild(selectedInfoRight);

    container.appendChild(selectedContainer);
    container.appendChild(minusButton);
    container.appendChild(timeSlider);
    container.appendChild(plusButton);
    container.appendChild(minusDatePickerContainer);
    container.appendChild(plusDatePickerContainer);
    map.getContainer().appendChild(container);

    $('#'+ this.id +' .'+ this.css).slider("destroy");
    $('#'+ this.id +' .'+ this.css).slider(sliderParams);

    var datePickerParamsMinus = datePickerParams;
    datePickerParamsMinus['defaultDate'] = this.start;
    datePickerParamsMinus['onClose'] = this.onStartChange;
    $('#'+ this.id +'MinusDatePicker').datepicker(datePickerParamsMinus);

    var datePickerParamsPlus = datePickerParams;
    datePickerParamsPlus['defaultDate'] = this.end;
    datePickerParamsPlus['onClose'] = this.onEndChange;
    $('#'+ this.id +'PlusDatePicker').datepicker(datePickerParamsPlus);

    this.selected = this.normalizeSelectedDate(this.selected);
    this.onStart(this.selected, this.range);
    return container;
}
TimeControl.prototype.normalizeSelectedDate = function(val) {
    var sel;
    if (this.range) {
        sel = [
            new Date(val[0] + this.yearStart,
                     this.start.getUTCMonth(),
                     this.start.getUTCDay()),
            new Date(val[1] + this.yearStart,
                     this.end.getUTCMonth(),
                     this.end.getUTCDay())
        ];
        formatedDate = [
            $.datepicker.formatDate(this.dateFormat, sel[0]),
            $.datepicker.formatDate(this.dateFormat, sel[1])
        ];
        $('#'+ this.id +'SelectedDate').html(formatedDate[0] +" : "+ formatedDate[1]);
    } else {
        sel = new Date(val + this.yearStart,
                       this.start.getUTCMonth(),
                       this.start.getUTCDay());
        formatedDate = $.datepicker.formatDate(this.dateFormat, sel);
        $('#'+ this.id +'SelectedDate').html(formatedDate);
    }
    return sel;
}
TimeControl.prototype.onStart = function(func) {
    this.onStart = this.timeStartHandler(func);
}
TimeControl.prototype.timeStartHandler = function(func) {
    var parent = this;
    return function(e, ui) {
        return func(parent.selected, parent.range);
    }
}
TimeControl.prototype.onTimeChange = function(func) {
    this.onTimeChange = this.timeChangeHandler(func);
}
TimeControl.prototype.timeChangeHandler = function(func) {
    var parent = this;
    return function(e, ui) {
        var selected = parent.normalizeSelectedDate(ui.values || ui.value);
        return func(selected, parent.range);
    }
}
TimeControl.prototype.onTimeMove = function(func) {
    this.onTimeMove = this.timeMoveHandler(func);
}
TimeControl.prototype.timeMoveHandler = function(func) {
    var parent = this;
    return function(e, ui) {
        var selected = parent.normalizeSelectedDate(ui.values || ui.value);
        return func(selected, parent.range);
    }
}
TimeControl.prototype.onStartChange = function(func) {
    this.onStartChange = this.startChangeHandler(func);
}
TimeControl.prototype.startChangeHandler = function(func) {
    var parent = this;
    return function(dateText, inst) {
        var date = $.datepicker.parseDate(parent.dateFormat, dateText);
        parent.yearStart = date.getUTCFullYear() || 1900;
        parent.max = Math.abs(parent.yearEnd - parent.yearStart);
        $('#'+ parent.id +' .'+ parent.css).slider("option", "max", parent.max);
        sliderOption = (this.range) ? 'values' : 'value';
        $('#'+ parent.id +' .'+ parent.css).slider("option", sliderOption, parent.selected);
        return func(date);
    }
}
TimeControl.prototype.onEndChange = function(func) {
    this.onEndChange = this.endChangeHandler(func);
}
TimeControl.prototype.endChangeHandler = function(func) {
    var parent = this;
    return function(dateText, inst) {
        var sliderOption, date = $.datepicker.parseDate(parent.dateFormat, dateText);
        parent.yearEnd = date.getUTCFullYear() || 2100;
        parent.max = Math.abs(parent.yearEnd - parent.yearStart);
        $('#'+ parent.id +' .'+ parent.css).slider("option", "max", parent.max);
        sliderOption = (this.range) ? 'values' : 'value';
        $('#'+ parent.id +' .'+ parent.css).slider("option", sliderOption, parent.selected);
        return func(date);
    }
}
TimeControl.prototype.getDefaultPosition = function() {
    return this.defaultPosition;
}
TimeControl.DAY = 1/(12*30);
TimeControl.MONTH = 1/12;
TimeControl.YEAR = 1;
TimeControl.DECADE = 10;
TimeControl.CENTURY = 100;
