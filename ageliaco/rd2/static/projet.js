var common_content_filter = '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info';
var common_jqt_config = {fixed:false,speed:'fast',mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}};


jQuery(function($){

    if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
        // it's not realistic to think we can deal with all the bugs
        // of IE 6 and lower. Fortunately, all this is just progressive
        // enhancement.
        return;
    }


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

    // edit dialog
    $('.editAuteurs').prepOverlay(
    {
            subtype: 'ajax',
            filter: common_content_filter,
            cssclass: 'overlay-editAuteurs',
            //formselector: 'form.kssattr-formname-@@edit',
            formselector: 'form',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
            redirect: $.plonepopups.redirectbasehref,
            closeselector: '[name="form.button.Cancel"]',
        width: '50%',
        }
    );

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