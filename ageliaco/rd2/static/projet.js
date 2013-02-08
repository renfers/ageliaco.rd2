var common_content_filter = '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info';
var common_jqt_config = {fixed:false,speed:'fast',mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}};

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
            redirect: $.plonepopups.redirectbasehref,
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
            formselector: 'form.kssattr-formname-@@edit',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            redirect: $.plonepopups.redirectbasehref,
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