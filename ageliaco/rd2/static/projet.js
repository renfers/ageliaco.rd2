var common_content_filter = '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info';
var common_jqt_config = {fixed:false,speed:'fast',mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}};

var prevnext = {
    formTabs: null,

    next: function() { prevnext.formTabs.data('tabs').next(); prevnext._scrollToTop(); },
    prev: function() { prevnext.formTabs.data('tabs').prev(); prevnext._scrollToTop(); },

    _scrollToTop: function() {
        $(window).scrollTop(prevnext.formTabs.closest('form').offset().top);  
    },

    showButtons: function(event, index) {
        var tabs = prevnext.formTabs.data('tabs'),
            index = typeof(index) === 'undefined' ? tabs.getIndex() : index,
            current = tabs.getTabs()[index],
            count = tabs.getTabs().length;

        $('#prevnext_previous').toggle(index !== 0);
        $('#prevnext_next').toggle(index !== (count - 1));

        $('.formControls:last :submit[name=form_submit]').toggle(index === )count - 1));
    },

    init: function() {
        var tabs;
        prevnext.formTabs = $('.formTabs');
        tabs = prevnext.formTabs.data('tabs');
        if (tabs.getTabs().length > 0) {
            if ($('fieldset#fieldset-distribution').length === 0)
                 return;
            $('.formControls:last :submit:first')
                .before($('<input id="prevnext_previous" class="context" ' +
                          '       type="button" value="" />')
                      .val('< Previous')
                      .click(prevnext.prev))
                .before(document.createTextNode(' '));
            $('.formControls:last :submit:first')
                .before($('<input id="prevnext_next" class="context" ' +
                          '       type="button" value="" />')
                      .val('Next >')
                      .click(prevnext.next))
                .before(document.createTextNode(' '));
            prevnext.showButtons();
            tabs.onClick(prevnext.showButtons);
        }
    }
};

$(prevnext.init());

// jQuery.extend(jQuery.tools.overlay.conf, 
//     {
//         fixed:false,
//         speed:'fast',
//         mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}
//     });
(function($) {
		
	// static constructs
	$.plonepopups = $.plonepopups || {};
    
    $.extend($.plonepopups,
        {
            // method to show error message in a noform
            // situation.
            noformerrorshow: function noformerrorshow(el, noform) {
                var o = $(el),
                    emsg = o.find('dl.portalMessage.error');
                if (emsg.length) {
                    o.children().replaceWith(emsg);
                    return false;
                } else {
                    return noform;
                }
            },
            // After deletes we need to redirect to the target page.
            redirectbasehref: function redirectbasehref(el, responseText) {
                var mo = responseText.match(/<base href="(\S+?)"/i);
                if (mo.length === 2) {
                    return mo[1];
                }
                return location;
            }
        });
})(jQuery);

jQuery(function($){

    if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
        // it's not realistic to think we can deal with all the bugs
        // of IE 6 and lower. Fortunately, all this is just progressive
        // enhancement.
        return;
    }


// delete dialog
//     $('a.delAuteur').prepOverlay(
//     {
//         subtype: 'ajax',
//         filter: common_content_filter,
//         formselector: '#content-core>#addform>form',
//         noform: function(el) {
//             return noformerrorshow(el, 'reload');
//         },
//         closeselector: '[name=form.buttons  .Cancel]',
//         width: '50%'
//     }
//     );

//     $('#portal-personaltools a[href$="/login"], #portal-personaltools a[href$="/login_form"], .discussion a[href$="/login"], .discussion a[href$="/login_form"]').prepOverlay(
//         {
//             subtype: 'ajax',
//             filter: common_content_filter,
//             cssclass: 'overlay-login',
//             formselector: 'form#login_form',
//             noform: 'redirect',
//             redirect: function (overlay, responseText) {
//                 var href = location.href;
//                 if (href.search(/pwreset_finish$/) >= 0) {
//                     return href.slice(0, href.length-14) + 'logged_in';
//                 } else {
//                     // look to see if there has been a server redirect
//                     var newTarget = $("<div>").html(responseText).find("base").attr("href");
//                     if ($.trim(newTarget) && newTarget !== location.href) {
//                         return newTarget;
//                     }
//                     // if not, simply reload
//                     return href;
//                 }
//             }
//         }
//     );
    // add dialog
//     $('a.editAuteurs').prepOverlay(
//     {
//         subtype: 'ajax',
//         //filter: common_content_filter,
//         cssclass: 'overlay-editAuteurs',
//         formselector: '.crud-form',
//             noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
//             redirect: $.plonepopups.redirectbasehref,
//             closeselector: '[name="form.button.Cancel"]',
//         width: '100%'
//     }
//     );
    // add dialog
    $('a.addAuteur').prepOverlay(
    {
        subtype: 'ajax',
        filter: common_content_filter,
        cssclass: 'overlay-addAuteur',
        formselector: 'kssattr-formname-++add++ageliaco.rd2.auteur, form[id="form"]',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            redirect: $.plonepopups.redirectbasehref,
            closeselector: '[name="form.button.Cancel"]',
        width: '50%'
    }
    );
    // Delete dialog
    $('a.delAuteur').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            cssclass: 'overlay-delAuteur',
            formselector: '#delete_confirmation',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            //redirect: $.plonepopups.redirectbasehref,
            redirect: function (overlay, responseText) {
                var href = location.href;
                if (href.search(/pwreset_finish$/) >= 0) {
                    return href.slice(0, href.length-14) + 'logged_in';
                } else {
                    // look to see if there has been a server redirect
                    var newTarget = $("<div>").html(responseText).find("base").attr("href");
                    if ($.trim(newTarget) && newTarget !== location.href) {
                        return newTarget;
                    }
                    // if not, simply reload
                    return href;
                }
            },
            closeselector: '[name="form.button.Cancel"]',
            width:'50%'
        }
    );
    // edit dialog
    $('a.editAuteur').prepOverlay(
    {
            subtype: 'ajax',
            filter: common_content_filter,
            cssclass: 'overlay-editAuteur',
            //formselector: 'form.kssattr-formname-@@edit',
            formselector: 'form',
        onClose: function(){
            window.location.reload(true);
        },

        onBeforeLoad: function() {

            // grab wrapper element inside content
            var wrap = this.getOverlay().find(".contentWrap");
                var href = location.href;

            // load the page specified in the trigger
            wrap.attr('src', this.getTrigger().attr("href"));
        },
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            //redirect: $.plonepopups.redirectbasehref,
            redirect: function (overlay, responseText) {
                return location.href;
                
            },
            closeselector: '[name="form.button.Cancel"]',
            width:'50%'
        }
    );
//         subtype: 'ajax',
//         filter: common_content_filter,
//         formselector: '#content-core>form',
//         noform: function(el) {
//             return noformerrorshow(el, 'reload');
//         },
//         closeselector: '[name=form.buttons.cancel]',
//         width: '50%'
//     }
//     );

    // Delete dialog
    $('a.deleteSketchLink').prepOverlay(
    {
        subtype: 'ajax',
        filter: common_content_filter,
        formselector: '#content-core>form',
        noform: function(el) {
            return noformerrorshow(el, 'reload');
        },
        closeselector: '[name=form.button.Cancel]',
        width: '50%'
    }
    );

    // address edit dialog
    $('a.editAddressLink').prepOverlay(
    {
        subtype: 'ajax',
        filter: common_content_filter,
        formselector: '#content-core>form',
        noform: function(el) {
            return noformerrorshow(el, 'reload');
        },
        closeselector: '[name=form.buttons  .Cancel]',
        width: '50%'
    }
    );
});