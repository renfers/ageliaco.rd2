var common_content_filter = '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info';
var common_jqt_config = {fixed:false,speed:'fast',mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}};

// jQuery.extend(jQuery.tools.overlay.conf, 
//     {
//         fixed:false,
//         speed:'fast',
//         mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}
//     });

// (function($) {
// 		
// 	// static constructs
// 	$.plonepopups = $.plonepopups || {};
//     
//     $.extend($.plonepopups,
//         {
//             // method to show error message in a noform
//             // situation.
//             noformerrorshow: function noformerrorshow(el, noform) {
//                 var o = $(el),
//                     emsg = o.find('dl.portalMessage.error');
//                 if (emsg.length) {
//                     o.children().replaceWith(emsg);
//                     return false;
//                 } else {
//                     return noform;
//                 }
//             },
//             // After deletes we need to redirect to the target page.
//             redirectbasehref: function redirectbasehref(el, responseText) {
//                 var mo = responseText.match(/<base href="(\S+?)"/i);
//                 if (mo.length === 2) {
//                     return mo[1];
//                 }
//                 return location;
//             }
//         });
// })(jQuery);

jQuery(function($){

    if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
        // it's not realistic to think we can deal with all the bugs
        // of IE 6 and lower. Fortunately, all this is just progressive
        // enhancement.
        return;
    }

// projet submission confirmation
// $('submit.soumissionprojet').prepOverlay({
//     var checkstr =  confirm('Votre projet ne sera plus modifiable! Cliquez sur l\'imprimante pour soumettre cette version à votre directeur!');
//     subtype: 'ajax',
//     filter: '#content>*',
//     closeselector: '[name=form.button.Cancel]'
//     });
// 
// $('submit.soumissionprojet').click(function(){
// var checkstr =  confirm('Votre projet ne sera plus modifiable ;-) Cliquez sur l\'imprimante pour soumettre cette version à votre directeur!');
// if(checkstr == true){
//     return true;
//   // do your code
// }else{
// return false;
// }
// });

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
// crud-form
    // edit dialog
//     $('a.editAuteurs').prepOverlay(
//     {
//         subtype: 'ajax',
//         filter: common_content_filter,
//         cssclass: 'overlay-addAuteurs',
//         filter: 'div[class="crud-form"]',
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
    $('a.addEvent').prepOverlay(
    {
        subtype: 'ajax',
        filter: common_content_filter,
        cssclass: 'overlay-addAuteur',
        formselector: 'kssattr-formname-++add++Event, form[id="form"]',
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
    $('.editAuteur').prepOverlay(
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