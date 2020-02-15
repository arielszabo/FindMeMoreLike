$().ready(function() {
    var options = {
        url: "static/only_titles.json",

        list: {
            match: {
                enabled: true
            },
            maxNumberOfElements: 10,
//            onSelectItemEvent: function() {
//                var value = $("#provider-json").getSelectedItemData().imdbID;
//
//            },
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

    $('[data-toggle="tooltip"]').tooltip({
        container: 'body',
        trigger: 'click ; hover ; focus'
    });


    $('#myModal').on('show.bs.modal	', function () {});

    $(".save-missing").click(function(){
        $.ajax({
      type: 'POST',
      url: "/save_missing_titles",
      data: {"imdb_link": $("#imdb_link").val()},
      // todo: add a warning if input is bad
      success: function(){
                    $("#success-alert").show();
                    setTimeout(function() { $("#success-alert").hide(); }, 6000);
                    },
      error: function(){
                    $("#danger-alert").show();
                    setTimeout(function() { $("#danger-alert").hide(); }, 8000);
                    }
    });
    });
});
