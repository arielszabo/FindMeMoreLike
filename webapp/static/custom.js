$().ready(function() {
    var options = {
        url: "static/title_and_id_mapping.json",

        getValue: "title",

        list: {
            match: {
                enabled: true
            },
            maxNumberOfElements: 10,
            onSelectItemEvent: function() {
                var value = $("#provider-json").getSelectedItemData().imdbid;

                $("#data-holder").val(value).trigger("change");
            },
        },
        highlightPhrase: true,

        theme: "bootstrap"
    };

    $("#provider-json").easyAutocomplete(options);

    $(".seen-checkbox").click(function(){
        $.ajax({
      type: 'POST',
      url: "/save_seen_checkbox",
      data: {"id": $(this).attr("id"), "status": $(this).is(":checked")}
//      success: TODO
//      error: TODO
    });
    });


});
