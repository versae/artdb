google.load('search', '1');
if (!window.jQuery) {
    google.load('jquery', '1.4.2');
}

google.setOnLoadCallback(function() {
    var $;
    if (window.jQuery) {
        $ = window.jQuery;
    } else {
        $ = jQuery.noConflict();
    }
    var className = "googleimagessearchinput";
    var searchControl = new google.search.SearchControl();
    var imageSearch = new google.search.ImageSearch();
    searchControl.addSearcher(imageSearch);

    $("."+ className).each(function() {
        var input = $(this);
        var idImageSearch = input.attr('id') +"_"+ className;
        var currentSearch = input.val();
        var imgInput = $("<img>");
        imgInput.attr("src", input.val());
        imgInput.css({
            "border": "none",
            "display": "block",
            "padding-left": "105px"
        });
        input.after(imgInput);
        var aImageSearch = $("<a>");
        aImageSearch.attr("href", "void(0)");
        aImageSearch.html("Google Images");
        aImageSearch.css({
            "padding": "2px 0 0 20px",
            "background": "transparent url(http://groups.google.com/group/yotu/attach/8cf1ebf75cbb5215/google.png?part=29&thumb=1) no-repeat 2px 2px"
        });
        aImageSearch.click(function() {
            divImagesSearch.toggle();
            imgInput.toggle();
            return false;
        });
        input.after(aImageSearch);

        var divImagesSearch = $("<div>");
        divImagesSearch.attr("id", idImageSearch);
        divImagesSearch.css("padding-left", "101px");
        aImageSearch.after(divImagesSearch);
        divImagesSearch.hide();

        searchControl.draw(document.getElementById(idImageSearch));
        if (currentSearch.substring(0, 4) != "http") {
            searchControl.execute(currentSearch);
        }
        $("a.gs-image").live("click", function() {
            var href = $(this).attr("href");
            input.val(href);
            imgInput.attr("src", href);
            divImagesSearch.hide();
            imgInput.show();
            $(this).focus();
            return false;
        });
    });
});
