$().ready(function() {
    function log( message ) {
      $( ".display_loading_message" ).text( message ).prependTo( "#log" );
      $( "#log" ).scrollTop( 0 );
    }

    $("#provider-json").autocomplete({
      source: "/get_available_titles",
      minLength: 2
    });

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
