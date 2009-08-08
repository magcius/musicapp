$(function() {
        $("#LoginForm").openid({
            img_path: 'http://openid-realselector.googlecode.com/svn/trunk/img/'
        });
        $(".FlashMessage div span")
            .append('<a href="#" class="CloseButton">&times;</a>')
            .find(".CloseButton")
            .click(function () {
                
                $.get({type: "GET",
                       url: "/ajax/remove_message/" + $(this).closest(".FlashMessage").attr("id"),
                       success: function(data) {
                           if (data == "t")
                               $(this).slideUp();
                       }
                })
        });
});