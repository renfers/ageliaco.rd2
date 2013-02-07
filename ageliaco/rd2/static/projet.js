var common_content_filter = '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info';
var common_jqt_config = {fixed:false,speed:'fast',mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}};

jQuery.extend(jQuery.tools.overlay.conf, common_jqt_config);

jQuery(function($) {


    // method to show error message in a noform
    // situation.
    function noformerrorshow(el, noform) {
        var o = $(el),
            emsg = o.find('dl.portalMessage.error');
        if (emsg.length) {
            o.children().replaceWith(emsg);
            return false;
        } else {
            return noform;
        }
    }

    // $('#siteaction-sitemap a').prepOverlay({
    //     subtype: 'iframe'
    // });

    // add dialog
    $('a.addAuteur').prepOverlay(
    {
        subtype: 'ajax',
        filter: common_content_filter,
        formselector: '#content-core>#addform>form',
        noform: function(el) {
            return noformerrorshow(el, 'reload');
        },
        closeselector: '[name=form.buttons.cancel]',
        width: '50%'
    }
    );
// Delete dialog
//    $('a.delAuteur').prepOverlay({
//        subtype: 'ajax',
//        filter: common_content_filter,
//        formselector: '#delete_confirmation',
//        noform: function(el) { return noformerrorshow(el, 'redirect'); },
//        redirect: redirectbasehref,
//        closeselector: '[name=form.button.Cancel]',
//        width:'50%'
//      });
    // Delete dialog
    $('a.delAuteur').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            cssclass: 'overlay-delete',
            formselector: '#delete_confirmation',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            redirect: $.plonepopups.redirectbasehref,
            closeselector: '[name="form.button.Cancel"]',
            width:'50%'
        }
    );
// delete dialog
//     $('#siteaction-contact a').prepOverlay(
//         {
//             subtype: 'ajax',
//             filter: common_content_filter,
//             cssclass: 'overlay-contact',
//             formselector: 'form[name="feedback_form"]',
//             noform: function(el) {return $.plonepopups.noformerrorshow(el, 'close');}
//         }
//     );
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
// 

//         noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
//         redirect: $.plonepopups.redirectbasehref,

    // edit dialog
    $('a.editAuteur').prepOverlay(
    {
        subtype: 'ajax',
        filter: common_content_filter,
        cssclass: 'overlay-editAuteur',
        formselector: '#content-core>form',
        noform: function(el) {return $.plonepopups.noformerrorshow(el, 'close');},
        redirect: $.plonepopups.redirectbasehref,
        closeselector: '[name="form.button.Cancel"]',
        width: '50%'
    }
    );
// 
//     // Delete dialog
//     $('a.deleteSketchLink').prepOverlay(
//     {
//         subtype: 'ajax',
//         filter: common_content_filter,
//         formselector: '#content-core>form',
//         noform: function(el) {
//             return noformerrorshow(el, 'reload');
//         },
//         closeselector: '[name=form.button.Cancel]',
//         width: '50%'
//     }
//     );
// 
//     // address edit dialog
//     $('a.editAddressLink').prepOverlay(
//     {
//         subtype: 'ajax',
//         filter: common_content_filter,
//         formselector: '#content-core>form',
//         noform: function(el) {
//             return noformerrorshow(el, 'reload');
//         },
//         closeselector: '[name=form.buttons  .Cancel]',
//         width: '50%'
//     }
//     );
});