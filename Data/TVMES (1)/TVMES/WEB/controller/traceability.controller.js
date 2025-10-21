sap.ui.define([
  "production/controller/BaseController",
  "../scripts/Utils",
  "sap/m/MessageBox",
  "sap/m/MessageToast",
  "sap/ui/model/json/JSONModel",
  "../scripts/formatter"
], function (BaseController, Utils, MessageBox, MessageToast, JSONModel, formatter) {
  "use strict";
  return BaseController.extend("production.controller.traceability", {
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

            this.appRefresh.attachPress(this.getActiveSFCInformation.bind(this));
            this.appRefresh.attachPress(this.connectWebSocket.bind(this));
            this.appResource.attachChange(this.getActiveSFCInformation.bind(this));
            this.appResource.attachChange(this.connectWebSocket.bind(this));
            this.appLanguage.attachChange(this.getActiveSFCInformation.bind(this));

      localStorage.selectedLanguage = this.appLanguage.getSelectedKey();
      var selectedResource = localStorage.selectedResource;
      localStorage.resourceType = "TRACEABILITY";
      var oParameters = oEvent.getParameters();
      this.connectWebSocket();
      this.getActiveSFCInformation();
      var barcodeInput = this.getView().byId("barcodeInput");
      if (barcodeInput.getValue() === undefined || barcodeInput.getValue() === "") {
        jQuery.sap.delayedCall(500, this, function () {
          barcodeInput.focus();
        });
      }
    },
    onSelectTab: function (oEvent) {
      this.selectedIconBarKey = oEvent.getSource().getSelectedKey();
      if (this.selectedIconBarKey === "shopOrderList") {
      } else if (this.selectedIconBarKey === "materialList") {
        this.getMaterialList();
      }
    },
    startSfc: function (oEvent) {
      var barcodeInput = oEvent.getSource(),
        resource = localStorage.selectedResource.split("-")[0].split(",")[1];
      if (barcodeInput.getValue().trim() === "" || barcodeInput.getValue() === undefined) {
        this.changeInfoText("trc.sfc.null", "Reject");
        return;
      }
      var request = {
        site: this.site,
        resource: resource,
        sfc: barcodeInput.getValue()
      };
      var inputJSONModel = new JSONModel();
      inputJSONModel.setData(request);
      var newElemJSON = inputJSONModel.getJSON();
      var xhttpStartSfc = Utils.xhttpPost(
        "/bekorest/restapi/traceabilityController/startSfc?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource,
        newElemJSON);
      if (JSON.parse(xhttpStartSfc.response).success) {
        this.changeInfoText(JSON.parse(xhttpStartSfc.response).messageCode, "Accept");
      } else {
        this.changeInfoText(JSON.parse(xhttpStartSfc.response).messageCode, "Reject");
        barcodeInput.setValue();
      }
      this.getActiveSFCInformation();
      this.getMaterialList();
    },
    getMaterialList: function () {
      var locale = this.appLanguage.getSelectedKey(),
        resource = localStorage.selectedResource.split("-")[0].split(",")[1];
      var uri = "/bekorest/restapi/traceabilityController/" + locale + "/getMaterialList?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource;
      var xhttpGetMaterialList = Utils.xhttpGet(uri);
      if (xhttpGetMaterialList.status === 200) {
        this.materialList = JSON
          .parse(xhttpGetMaterialList.responseText);
      } else {
        this.materialList = [];
      }
      if (this.materialList.find(x => x.barcode === 'N')) {
        this.materialList.find(x => x.barcode === 'N').selected = "Y";
      }
      var filteredData = this.materialList.filter(x => x.barcode !== 'N')
      Object.keys(filteredData).map(
        function (object) {
          filteredData[object]["selected"] = "N"
        });
      this.materialListModel = new JSONModel();
      this.materialListModel.setSizeLimit(10000);
      this.materialListModel.setData(this.materialList);
      this.getView().setModel(this.materialListModel,
        "materialListModel");
      this.getView().getModel("materialListModel").refresh(true);
      this.getView().byId("materialListTable").getModel("materialListModel").refresh(true);
      $("[id*=materialListTable]").off("selectstart", "tr").on("selectstart", "tr", this.focusFirstInput.bind(this));
      this.focusFirstInput();
    },
    focusFirstInput: function () {
      var oTable = this.getView().byId("materialListTable");
      if (oTable.getSelectedItem()) {
        jQuery.sap.delayedCall(1000, this, function () {
          oTable.getSelectedItem().getAggregation("cells").findLast(x => x.getItems()).getAggregation("items").find(y => y.getProperty("type") === "Text").focus();
        });
      }
    },
    completeSfc: function () {
      var barcodeInput = this.getView().byId("barcodeInput"),
        resource = localStorage.selectedResource.split("-")[0].split(",")[1];
      var request = {
        site: this.site,
        resource: resource
      };
      var inputJSONModel = new JSONModel();
      inputJSONModel.setData(request);
      var newElemJSON = inputJSONModel.getJSON();
      var xhttpCompleteSfc = Utils.xhttpPost(
        "/bekorest/restapi/traceabilityController/completeSfc?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource,
        newElemJSON);
      if (JSON.parse(xhttpCompleteSfc.response).success) {
        this.changeInfoText(JSON.parse(xhttpCompleteSfc.response).messageCode, "Accept");
        barcodeInput.setValue();
        jQuery.sap.delayedCall(500, this, function () {
          barcodeInput.focus();
        });

      } else {
        this.changeInfoText(JSON.parse(xhttpCompleteSfc.response).messageCode, "Reject");
      }
      this.getActiveSFCInformation();
      this.getMaterialList();
    },
    onScanBarcode: function (oEvent) {
      var barcodeInput = oEvent.getSource(),
        selectedObject = oEvent.getSource().getBindingContext("materialListModel").getObject(),
        resource = localStorage.selectedResource.split("-")[0].split(",")[1];
      if (barcodeInput.getValue().trim() === "" || barcodeInput.getValue() === undefined) {
        this.changeInfoText("trc.sfc.null", "Reject");
        return;
      }
      var request = {
        site: this.site,
        resource: resource,
        barcode: barcodeInput.getValue(),
        quantity: selectedObject.quantity,
        bomRef: selectedObject.bomRef,
        itemRef: selectedObject.itemRef
      };
      var inputJSONModel = new JSONModel();
      inputJSONModel.setData(request);
      var newElemJSON = inputJSONModel.getJSON();
      var xhttpAssembleComponent = Utils.xhttpPost(
        "/bekorest/restapi/traceabilityController/assembleComponent?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource,
        newElemJSON);
      if (!JSON.parse(xhttpAssembleComponent.response).error) {
        this.changeInfoText(JSON.parse(xhttpAssembleComponent.response).message, (JSON.parse(xhttpAssembleComponent.response).errorCode === 0 ? "Accept" : "Warning"));
      } else {
        this.changeInfoText(JSON.parse(xhttpAssembleComponent.response).message, "Reject");
      }
      this.getMaterialList();
    },
    onPressDisassemble: function (oEvent) {
      var barcodeInput = oEvent.getSource(),
        selectedObject = oEvent.getSource().getBindingContext("materialListModel").getObject(),
        resource = localStorage.selectedResource.split("-")[0].split(",")[1];
      var request = {
        site: this.site,
        resource: resource,
        quantity: selectedObject.quantity,
        itemRef: selectedObject.itemRef,
        sfcAssyRef: selectedObject.sfcassyRef
      };
      var inputJSONModel = new JSONModel();
      inputJSONModel.setData(request);
      var newElemJSON = inputJSONModel.getJSON();
      var xhttpDisassembleComponent = Utils.xhttpPost(
        "/bekorest/restapi/traceabilityController/disassembleComponent?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource,
        newElemJSON);
      if (JSON.parse(xhttpDisassembleComponent.response).success) {
        this.changeInfoText(JSON.parse(xhttpDisassembleComponent.response).messageCode, "Accept");
      } else {
        this.changeInfoText(JSON.parse(xhttpDisassembleComponent.response).messageCode, "Reject");
      }
      var oInput = oEvent.getSource().getParent().getAggregation("items").filter(x => x._buttonPressed === undefined)[0];
      oInput.setValue("");
      this.getMaterialList();
    }
  })
});