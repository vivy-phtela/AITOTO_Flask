$(document).ready(function () {
    $('.hamburger').click(function (e) {
        let menu = $(this).closest('.header-sticky')
        let toggle = $('#hamburger-toggle')

        if (!toggle.hasClass('close')) {
            toggle.removeClass('bars')
            toggle.addClass('close')
            menu.addClass('open')
        } else {
            toggle.removeClass('close')
            toggle.addClass('bars')
            menu.removeClass('open')
        }

        e.preventDefault()
    })
})