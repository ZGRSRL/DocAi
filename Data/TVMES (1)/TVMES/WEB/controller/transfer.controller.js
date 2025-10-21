sap.ui.define([
  "production/controller/BaseController",
  "../scripts/Utils",
  "sap/m/MessageBox",
  "sap/m/MessageToast",
  "sap/ui/model/json/JSONModel",
  "../scripts/formatter"
], function (BaseController, Utils, MessageBox, MessageToast, JSONModel, formatter) {
  "use strict";
  return BaseController.extend("production.controller.transfer", {
    formatter: formatter,
    onInit: function () {
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
      this.appWorkCenter = this.appView.byId("idWorkcenterCombo");
      this.appResource = this.appView.byId("idResrceCombo");
      this.appRefresh = this.appView.byId("idRefresh");
      this.appLanguage = this.appView.byId("idLanguageCombo");
      this.site = this.getPlant();
      this.getActiveSFCInformation();
      var barcodeInput = this.getView().byId("barcodeInput");
      if (barcodeInput.getValue() === undefined || barcodeInput.getValue() === "") {
        jQuery.sap.delayedCall(500, this, function () {
          barcodeInput.focus();
        });
      }
      var selectedResource = localStorage.selectedResource;
      localStorage.resourceType = "TYPE_LABEL";
      var oParameters = oEvent.getParameters();
      this.connectWebSocket();
      this.loadShopOrders();
            this.appRefresh.attachPress(this.getActiveSFCInformation.bind(this));
            this.appRefresh.attachPress(this.connectWebSocket.bind(this));
            this.appResource.attachChange(this.getActiveSFCInformation.bind(this));
            this.appResource.attachChange(this.connectWebSocket.bind(this));
            this.appLanguage.attachChange(this.getActiveSFCInformation.bind(this));
      if (localStorage.refreshInterval) {
        clearInterval(localStorage.refreshInterval);
      }
      localStorage.refreshInterval = setInterval(this.refreshActiveTableData.bind(this), 1200000);
    },
    onSelectTab: function (oEvent) {
      this.selectedIconBarKey = oEvent.getSource().getSelectedKey();
      if (this.selectedIconBarKey === "shopOrderList") {
      } else if (this.selectedIconBarKey === "materialList") {
        this.getTransferredList();
      }
    },
    getTransferredList: function () {
      var locale = this.appLanguage.getSelectedKey(),
        resource = localStorage.selectedResource.split("-")[0].split(",")[1];
      var uri = "/bekorest/restapi/confirmationController/getTransferredSfcs?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource;
      var xhttpGetTransferredList = Utils.xhttpGet(uri);
      if (xhttpGetTransferredList.status === 200) {
        this.transferredList = JSON
          .parse(xhttpGetTransferredList.responseText);
      } else {
        this.transferredList = [];
      }
      this.transferredListModel = new JSONModel();
      this.transferredListModel.setSizeLimit(10000);
      this.transferredListModel.setData(this.transferredList);
      this.getView().setModel(this.transferredListModel,
        "transferredListModel");
      this.getView().getModel("transferredListModel").refresh(true);
    },
    onScanBarcode: function (oEvent) {
      var barcodeInput = oEvent.getSource(),
        resource = localStorage.selectedResource.split("-")[0].split(",")[1];
      if (barcodeInput.getValue().trim() === "" || barcodeInput.getValue() === undefined) {
        this.changeInfoText("trc.sfc.null", "Reject");
        return;
      }
      // this.getView().byId("listItemSfc").setValue(barcodeInput.getValue());
      var request = {
        site: this.site,
        workCenter: this.appWorkCenter.getSelectedKey(),
        resource: resource,
        sfc: barcodeInput.getValue()
      };
      var inputJSONModel = new JSONModel();
      inputJSONModel.setData(request);
      var newElemJSON = inputJSONModel.getJSON();
      var xhttpTransferSfc = Utils.xhttpPost(
        "/bekorest/restapi/confirmationController/sendTransfer?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource,
        newElemJSON);
      if (!JSON.parse(xhttpTransferSfc.response).error) {
        this.changeInfoText(JSON.parse(xhttpTransferSfc.response).messageCode, (JSON.parse(xhttpTransferSfc.response).errorCode === 0 ? "Accept" : "Warning"));
        this.getTransferredList();
        barcodeInput.setValue("");
      } else {
        this.changeInfoText(JSON.parse(xhttpTransferSfc.response).messageCode, "Reject");
        barcodeInput.setValue("");
      }
    }
  })
});