sap.ui.define([
  "production/controller/BaseController",
  "production/scripts/Utils",
  "sap/m/MessageBox",
  "sap/m/MessageToast",
  "sap/ui/model/json/JSONModel",
  "../scripts/formatter"
], function (BaseController, Utils, MessageBox, MessageToast, JSONModel, formatter) {
  "use strict";
  var appView;
  var messageData;
  return BaseController.extend("production.controller.typeLabel", {
    formatter: formatter,
    onInit: function () {
      this.setInputOrder(["barcodeInput"]);
      this.getRouter().attachRoutePatternMatched(this.onRouteMatched, this);
      this.messageData = {
        infoMessage: "firstMessage.notification.label",
        infoMessageType: "Accept",
        notificationMessage: "firstMessage.notification.label",
        notificationMessageType: "Accept",
      }
      let oModel = new JSONModel();
      oModel.setData(this.messageData);
      this.getView().setModel(oModel, "messageModel");
      this.setGeneralInfoMessageComp(this.getView().byId("idGeneralInfoMessages"));
      this.setNotificationMessageComp(this.getView().byId("idInfoMessages"));
    },
    onRouteMatched: function (oEvent) {

      this.appView = sap.ui.core.Component.getOwnerComponentFor(this.getView()).getRootControl();
      var appWorkCenter = this.appView.byId("idWorkcenterCombo");
      var appResource = this.appView.byId("idResrceCombo");
      var appRefresh = this.appView.byId("idRefresh");
      var appLanguage = this.appView.byId("idLanguageCombo");
      var selectedResource = localStorage.selectedResource;
      localStorage.resourceType = "TYPE_LABEL";
      var oParameters = oEvent.getParameters();
      this.connectWebSocket();
      this.getActiveSFCInformation();
      appRefresh.attachPress(this.getActiveSFCInformation.bind(this));
      appRefresh.attachPress(this.connectWebSocket.bind(this));
      appResource.attachChange(this.getActiveSFCInformation.bind(this));
      appResource.attachChange(this.connectWebSocket.bind(this));
      appLanguage.attachChange(this.getActiveSFCInformation.bind(this));
      appLanguage.attachChange(this.connectWebSocket.bind(this));
      if (localStorage.refreshInterval) {
        clearInterval(localStorage.refreshInterval);
      }
      localStorage.refreshInterval = setInterval(this.refreshActiveTableData.bind(this), 1200000);
    },
    closeBarcodeForPrintDialog: function () {
      this.getView().byId("idCreateBarcodeForPrintDialog").destroy();
    },

    onExit: function () {
      appRefresh.detachPress(this.loadShopOrders.bind(this))
      appResource.detachChange(this.loadShopOrders.bind(this));
      appResource.detachChange(this.connectWebSocket.bind(this));
      this.closeConnection();
      this.getRouter().detachRouteMatched(this.onRouteMatched, this);
    },
    onSubmitStartSfc: function (oEvent) {
      let sfc = this.getView().byId("sfcInput").getValue();
      let params = {
        site: this.getPlant(),
        locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
        resource: localStorage.selectedResource.split("-")[0].split(",")[1],
        workcenter: localStorage.selectedWorkCenter,
        sfc: sfc
      };
      var endPoint = "/typeLabelController/startSfc";
      var buildUrl = Utils.buildUrl(endPoint, params);
      Utils.asyncPOST(buildUrl, function (response) {
        if (response.success) {
          if (response.messageCode) {
            this.changeInfoText(response.messageCode, "Accept");
          }
          this.getActiveSFCInformation();
        } else {
          this.getActiveSFCInformation();
          if (response.messageCode) {
            
             this.getView().byId("sfcInput").setValue("");
            this.changeInfoText(response.messageCode, "Reject");
          }
        }
      }.bind(this));
      //this.getActiveSFCInformation();
    },
    onSubmitSerializeSfcLabel: function (oEvent) {
      let barcode = this.getView().byId("barcodeInput").getValue();
      let sfcInput = this.getView().byId("sfcInput").getValue();
      let params = {
        site: this.getPlant(),
        locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
        resource: localStorage.selectedResource.split("-")[0].split(",")[1],
        workcenter: localStorage.selectedWorkCenter,
        barcode: barcode
      };
      var endPoint = "/typeLabelController/completeSFCBarcode";
      var buildUrl = Utils.buildUrl(endPoint, params);
      Utils.asyncPOST(buildUrl, function (response) {
        if (response.messageCode == undefined) {
          this.changeInfoText("29989.error.label", "Reject");
        }
        if (response.success) {
          if (response.messageCode) {
            this.getActiveSFCInformation();
            this.setFocusWithId("sfcInput");
            this.changeInfoText(response.messageCode, "Accept");
            this.clearInput();
          }
        } else {
          if (response.messageCode) {
            this.getActiveSFCInformation();
            this.changeInfoText(response.messageCode, "Reject");
          }
        }
      }.bind(this));
    },
    clearInput: function () {
      this.getView().byId("barcodeInput").setValue("");
      this.getView().byId("sfcInput").setValue("");
    }
  })
});
