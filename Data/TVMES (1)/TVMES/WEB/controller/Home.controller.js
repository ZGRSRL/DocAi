sap.ui.define([
    "production/controller/BaseController"
], function (BaseController) {
    "use strict";

    return BaseController.extend("production.controller.Home", {

        onDisplayNotFound: function () {
            // display the "notFound" target without changing the hash
            this.getRouter().getTargets().display("notFound", {
                fromTarget: "home"
            });
        },

        onNavToPanel: function () {
            this.getRouter().navTo("panelView");
        },
       onNavToTraceability: function () {
            this.getRouter().navTo("traceabilityView");
        },
       onNavToTypeLabel: function () {
            this.getRouter().navTo("typeLabelView");
        }, onNavToRepair: function () {
            this.getRouter().navTo("repairView");
        },
        onNavToQualityChain: function () {
            this.getRouter().navTo("qualityChainView");
        },
	   onNavToConfirmation: function () {
            this.getRouter().navTo("confirmationView");
        },
onNavToPackageLabel:function(){
            this.getRouter().navTo("packageLabelView");
},
onNavToTransfer: function () {
            this.getRouter().navTo("transferView");
        }
    });

});
