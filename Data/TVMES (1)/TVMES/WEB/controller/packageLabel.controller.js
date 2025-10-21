sap.ui.define([
    "production/controller/BaseController",
    "../scripts/Utils",
    "sap/m/MessageBox",
    "sap/m/MessageToast",
    "sap/ui/model/json/JSONModel",
    "../scripts/formatter"
], function (BaseController, Utils, MessageBox, MessageToast, JSONModel, formatter) {
    "use strict";
    return BaseController.extend("production.controller.packageLabel", {
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
            this.appView = this.getOwnerComponent().getRootControl();
            this.appWorkCenter = this.appView.byId("idWorkcenterCombo");
            this.appResource = this.appView.byId("idResrceCombo");
            this.appRefresh = this.appView.byId("idRefresh");
            this.appLanguage = this.appView.byId("idLanguageCombo");
            localStorage.selectedLanguage = this.appLanguage.getSelectedKey()

            this.site = this.getPlant();
            this.getActiveSFCInformation();
            var barcodeInput = this.getView().byId("barcodeInput");
            if (barcodeInput) {
                if (barcodeInput.getValue() === undefined || barcodeInput.getValue() === "") {
                    jQuery.sap.delayedCall(500, this, function () {
                        barcodeInput.focus();
                    });
                }
            }
            var selectedResource = localStorage.selectedResource;
            localStorage.resourceType = "PACKAGE_LABEL";
            var oParameters = oEvent.getParameters();
            this.connectWebSocket();
            this.appRefresh.attachPress(this.getActiveSFCInformation.bind(this));
            this.appRefresh.attachPress(this.connectWebSocket.bind(this));
            this.appResource.attachChange(this.getActiveSFCInformation.bind(this));
            this.appResource.attachChange(this.connectWebSocket.bind(this));
            this.appLanguage.attachChange(this.getActiveSFCInformation.bind(this));

            let sfcInfoLabel = this.getView().byId("activeSFCInfo");
            sfcInfoLabel.addEventDelegate({
                onAfterRendering: function (param) {
                    this.changeTestButton(param.srcControl.getValue());
                }.bind(this)
            });
            let messageButton = this.getView().byId("idInfoMessages");
            messageButton.addEventDelegate({
                onAfterRendering: function () {
                    this.changeTestButton(this.podHDRData.SFC);
                }.bind(this)
            });

            if (localStorage.refreshInterval) {
                clearInterval(localStorage.refreshInterval);
            }
            localStorage.refreshInterval = setInterval(this.refreshActiveTableData.bind(this), 1200000);
        },
        changeTestButton: function (sfc) {
            let testButton = this.getView().byId("testNOKButton");
            try {
                testButton.removeStyleClass("orangeGlow");
                testButton.removeStyleClass("greenGlow");
                testButton.removeStyleClass("blueGlow");
                if (sfc == "" || sfc == '' || sfc == undefined || sfc == null || this.podHDRData.TEST_OK == undefined) {
                    testButton.setType("Emphasized");
                    testButton.setText("Test Result");
                    testButton.addStyleClass("blueGlow");
                    return;
                }
                if (this.podHDRData.TEST_OK == false || this.podHDRData.TEST_OK == "false") {
                    testButton.setType("Warning");
                    testButton.setText("Test NOK");
                    testButton.addStyleClass("orangeGlow");
                    testButton.remove
                    return;
                }
                if (this.podHDRData.TEST_OK == true || this.podHDRData.TEST_OK == "true") {
                    testButton.setType("Accept");
                    testButton.setText("Test OK");
                    testButton.addStyleClass("greenGlow");
                    return;
                }
            } catch (e) {
                testButton.setType("Emphasized");
                testButton.setText("Test Result");
                testButton.addStyleClass("blueGlow");
            }

        },
        onSelectTab: function (oEvent) {
            this.selectedIconBarKey = oEvent.getSource().getSelectedKey();
            if (this.selectedIconBarKey === "shopOrderList") {
            } else if (this.selectedIconBarKey === "materialList") {
                this.getMaterialList();
            } else if (this.selectedIconBarKey === "nc") {
                // Open login dialog when NC tab is selected
                this.openLoginDialog();
            } else if (this.selectedIconBarKey == "allMaterialList")
                this.getAllMaterialList();
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
            this.focusFirstInput("materialListTable");
        },
        getAllMaterialList: function () {
            var locale = this.appLanguage.getSelectedKey(),
                resource = localStorage.selectedResource.split("-")[0].split(",")[1];
            var uri = "/bekorest/restapi/packageLabelController/" + locale + "/getAllMaterialList?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource;
            var xhttpGetMaterialList = Utils.xhttpGet(uri);
            if (xhttpGetMaterialList.status === 200) {
                this.allMaterialList = JSON
                    .parse(xhttpGetMaterialList.responseText);
            } else {
                this.allMaterialList = [];
            }
            if (this.allMaterialList.find(x => x.barcode === 'N')) {
                this.allMaterialList.find(x => x.barcode === 'N').selected = "Y";
            }
            var filteredData = this.allMaterialList.filter(x => x.barcode !== 'N')
            Object.keys(filteredData).map(
                function (object) {
                    filteredData[object]["selected"] = "N"
                });
            this.allMaterialListModel = new JSONModel();
            this.allMaterialListModel.setSizeLimit(10000);
            this.allMaterialListModel.setData(this.allMaterialList);
            this.getView().setModel(this.allMaterialListModel,
                "allMaterialListModel");
            this.getView().getModel("allMaterialListModel").refresh(true);
            $("[id*=materialListTable]").off("selectstart", "tr").on("selectstart", "tr", this.focusFirstInput.bind(this));
            this.focusFirstInput("allMaterialListTable");
        },
        focusFirstInput: function (tableId) {
            var oTable = this.getView().byId(tableId);
            if (oTable.getSelectedItem()) {
                jQuery.sap.delayedCall(500, this, function () {
                    oTable.getSelectedItem().getAggregation("cells").findLast(x => x.getItems()).getAggregation("items").find(y => y.getProperty("type") === "Text").focus();
                });
            }
        },
        completeSfc: function () {
            var barcodeInput = this.getView().byId("sfcInput"),
                resource = localStorage.selectedResource.split("-")[0].split(",")[1];
            var request = {
                site: this.site,
                resource: resource,
                sfc: this.podHDRData.SFC
            };
            var inputJSONModel = new JSONModel();
            inputJSONModel.setData(request);
            var newElemJSON = inputJSONModel.getJSON();
            var xhttpCompleteSfc = Utils.xhttpPost(
                "/bekorest/restapi/qualityChainController/qualityCompleteSfc?site=" + this.site,
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
            if (selectedObject == undefined)
                oEvent.getSource().getBindingContext("allMaterialListModel").getObject()
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
            if (JSON.parse(xhttpAssembleComponent.response).success) {
                this.changeInfoText(JSON.parse(xhttpAssembleComponent.response).messageCode, (JSON.parse(xhttpAssembleComponent.response).errorCode === 0 ? "Accept" : "Warning"));
            } else {
                this.changeInfoText(JSON.parse(xhttpAssembleComponent.response).messageCode, "Reject");
            }
            this.getMaterialList();
        },
        onPressDisassemble: function (oEvent) {
            let barcodeInput = oEvent.getSource();
            let oBindingContext = oEvent.getSource().getBindingContext("materialListModel");
            if (!oBindingContext) oBindingContext = oEvent.getSource().getBindingContext("allMaterialListModel");
            let selectedObject = oBindingContext.getObject();
            let resource = localStorage.selectedResource.split("-")[0].split(",")[1];
            if (selectedObject == undefined)
                selectedObject = oEvent.getSource().getBindingContext("allMaterialListModel").getObject()
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
            if (this.getView().byId("idIconTabBar").getSelectedKey() == "allMaterialList")
                this.getAllMaterialList();
            if (this.getView().byId("idIconTabBar").getSelectedKey() == "materialList")
                this.getMaterialList();
        },
        onSelectMaterialTable: function (oEvent) {
            if (oEvent.getParameter("listItem").getBindingContext("materialListModel").getObject().barcode === 'N') {
                var materialListModel = this.getView().getModel("materialListModel").getData();
                Object.keys(materialListModel).map(
                    function (object) {
                        if (materialListModel[object]["barcode"] === 'N') {
                            materialListModel[object]["selected"] = "U"
                        }
                    });
                oEvent.getParameter("listItem").getBindingContext("materialListModel").getObject().selected = "Y";

                this.getView().getModel("materialListModel").refresh(true);
                this.focusFirstInput("materialListTable");
            }
        },
        onSelectAllMaterialTable: function (oEvent) {
            if (oEvent.getParameter("listItem").getBindingContext("allMaterialListModel").getObject().barcode === 'N') {
                var materialListModel = this.getView().getModel("allMaterialListModel").getData();
                Object.keys(materialListModel).map(
                    function (object) {
                        if (materialListModel[object]["barcode"] === 'N') {
                            materialListModel[object]["selected"] = "U"
                        }
                    });
                oEvent.getParameter("listItem").getBindingContext("allMaterialListModel").getObject().selected = "Y";

                this.getView().getModel("allMaterialListModel").refresh(true);
                this.focusFirstInput("allMaterialListTable");
            }
        },
        onPressTestOK: function () {
            let userRequest = Utils.whoAmI();
            let whoAmI = Utils.extractIllumLoginName(userRequest.response);
            if (!whoAmI) {
                MessageToast.show("Kullanıcı bilgisi alınamadı.");
                whoAmI = "TV_USER";
            }

            let request = {
                site: this.site,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                sfc: this.podHDRData.SFC,
                user: whoAmI
            };
            var inputJSONModel = new JSONModel();
            inputJSONModel.setData(request);
            var newElemJSON = inputJSONModel.getJSON();
            var xhttpTestOK = Utils.xhttpPost(
                "/bekorest/restapi/qualityChainController/testOK?site=" + this.site, newElemJSON);
            if (JSON.parse(xhttpTestOK.response).success) {
                this.changeInfoText(JSON.parse(xhttpTestOK.response).messageCode, "Accept");
            } else {
                this.changeInfoText(JSON.parse(xhttpTestOK.response).messageCode, "Reject");
            }
        },
        // Handle login button press
        onPressNCDialogLogin: function () {
            /*if (this.podHDRData.SFC === "-" || this.podHDRData.SFC === undefined || this.podHDRData.SFC === "") {
                MessageToast.show("SFC bilgisi alınamadı.");
                return;
            }*/
            var sUsername = sap.ui.getCore().byId("idNCDialogUsername").getValue();
            var sPassword = sap.ui.getCore().byId("idNCDialogPassword").getValue();

            // Perform login validation here
            if (sUsername && sPassword) {
                let request = Utils.getFormIDLogin(sUsername, sPassword);
                console.log(request);
                if (request.status == 401) {
                    MessageToast.show("Kullanıcı adı/ Şifre yanlış");
                    return;
                }
                if (!request.getResponseHeader("content-type").includes("application/json")) {
                    MessageToast.show("Kullanıcı adı/ Şifre yanlış");
                    return;
                }
                if (request.status == 200) {

                    var response = JSON.parse(request.responseText);
                    if (response.FORM_ID) {
                        let xHttpLoginUser;
                        try {
                            xHttpLoginUser = Utils.xhttpPost("/bekorest/restapi/qualityChainController/loginUser?site="
                                + this.site + "&user=" + sUsername, {});
                        }
                        catch (e) {
                            MessageToast.show("NC Login failed: " + e);
                            return;
                        }
                        if (JSON.parse(xHttpLoginUser.response).success) {
                            localStorage.lastLoggedInUser = sUsername;
                            this._oNCLoginDialog.close();
                            if (localStorage.selectedLoginID.includes("reprintLabel"))
                                this.onPressReprintSFC();
                            else
                                this._openReasonCodesDialog();
                        } else {
                            MessageToast.show("Kullanıcıya izin verilmedi.");
                            return;
                        }

                    } else {
                        MessageToast.show("Kullanıcı adı/ Şifre yanlış");
                        return;
                    }


                }
            } else {
                MessageToast.show("Please enter both username and password");
            }

        },
        onSubmitStartSfc: function (oEvent) {
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
                "/bekorest/restapi/packageLabelController/packageStartSfc?site=" + this.site, newElemJSON);
            if (JSON.parse(xhttpStartSfc.response).success) {
                this.changeInfoText(JSON.parse(xhttpStartSfc.response).messageCode, "Accept");
            } else {
                this.changeInfoText(JSON.parse(xhttpStartSfc.response).messageCode, "Reject");
                barcodeInput.setValue();
            }
            this.getActiveSFCInformation();
            this.getMaterialList();
        },
        onPressComplete: function () {
            let request = {
                site: this.site,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                sfc: this.podHDRData.SFC
            };
            var inputJSONModel = new JSONModel();
            inputJSONModel.setData(request);
            var newElemJSON = inputJSONModel.getJSON();
            var xhttpCompleteSfc = Utils.xhttpPost(
                "/bekorest/restapi/packageLabelController/packageCompleteSfc?site=" + this.site, newElemJSON);
            if (JSON.parse(xhttpCompleteSfc.response).success) {
                this.changeInfoText(JSON.parse(xhttpCompleteSfc.response).messageCode, "Accept");
            } else {
                this.changeInfoText(JSON.parse(xhttpCompleteSfc.response).messageCode, "Reject");
            }
            this.getActiveSFCInformation();
        },
        onPressReasonCodesAccept: function () {
            let userRequest = Utils.whoAmI();
            let whoAmI = Utils.extractIllumLoginName(userRequest.response);
            if (!whoAmI) {
                MessageToast.show("Kullanıcı bilgisi alınamadı.");
                whoAmI = "TV_USER";
            }

            let request = {
                site: this.site,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                workCenter: this.appWorkCenter.getSelectedKey(),
                shopOrder: this.podHDRData.SHOP_ORDER,
                user: whoAmI,
                sfc: this.podHDRData.SFC,
                reasonCodes: this.getView().getModel("ncReasonCodesModel").getData()
            };
            var inputJSONModel = new JSONModel();
            inputJSONModel.setData(request);
            var newElemJSON = inputJSONModel.getJSON();
            let xhttpReasonCodesAccept = Utils.xhttpPost("/bekorest/restapi/qualityChainController/saveReasonCodes?site=" + this.site, newElemJSON);
            if (JSON.parse(xhttpReasonCodesAccept.response).success) {
                this.changeInfoText(JSON.parse(xhttpReasonCodesAccept.response).messageCode, "Accept");
            } else {
                this.changeInfoText(JSON.parse(xhttpReasonCodesAccept.response).messageCode, "Reject");
            }
            this.getView().byId("reasonCodesDialog").destroy();
        },
        onPressReasonCodesCancel: function () {
            this.getView().byId("reasonCodesDialog").destroy();
        },
        _openReasonCodesDialog: function (oEvent) {
            var oView = this.getView();
            var oDialog = oView.byId("idCreateBarcodeForPrintDialog");
            if (!oDialog) {
                oDialog = sap.ui.xmlfragment(oView.getId(),
                    "production.fragments.reasonCodes", this
                );
                oView.addDependent(oDialog);
            }


            let params = {
                site: this.site,
                sfc: this.podHDRData.SFC,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1]
            };
            var inputJSONModel = new JSONModel();
            inputJSONModel.setData(params);
            var newElemJSON = inputJSONModel.getJSON();
            var getReasonCodesRequest = Utils.xhttpPost(
                "/bekorest/restapi/qualityChainController/getReasonCodes?site=" + this.site, newElemJSON);
            let data = JSON.parse(getReasonCodesRequest.response)
            if (data.errorCode) {
                this.changeInfoText(JSON.parse(callRequest.response).messageCode, "Reject");
                return;
            }
            this.ncReasonCodesModel = new JSONModel();
            this.ncReasonCodesModel.setSizeLimit(10000);
            this.ncReasonCodesModel.setData(data.reasonCodes.filter(x => x.locale == localStorage.selectedLanguage));
            this.getView().setModel(this.ncReasonCodesModel,
                "ncReasonCodesModel");
            this.getView().getModel("ncReasonCodesModel").refresh(true);
            oDialog.open();
        },
        openLoginDialog: function (oEvent) {
            localStorage.selectedLoginID = oEvent.getSource().getId();
            this.getOwnerComponent().byId("traceabilityView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this.getOwnerComponent().byId("repairView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this.getOwnerComponent().byId("qualityChainView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this.getOwnerComponent().byId("packageLabelView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this._oNCLoginDialog = sap.ui.xmlfragment("production.fragments.qwertyKeyboard", this);
            this.getView().addDependent(this._oNCLoginDialog);

            // Reset input fields
            var usernameInput = sap.ui.getCore().byId("idNCDialogUsername");
            var passwordInput = sap.ui.getCore().byId("idNCDialogPassword");

            usernameInput.setValue("");
            passwordInput.setValue("");

            // Initialize shift state to false (lowercase)
            this._shiftEnabled = false;

            // Set initial active input to username field
            this._activeNCInput = usernameInput;

            // Update active input indicator
            var indicator = sap.ui.getCore().byId("activeInputIndicator");
            if (indicator) {
                indicator.setText("Aktif Alan: Kullanıcı Adı");
            }

            // Open dialog
            this._oNCLoginDialog.open();

            // Use a timeout to ensure the dialog is rendered before focusing
            jQuery.sap.delayedCall(400, this, function () {
                usernameInput.focus();
            });
        },
        onSendNCCodes: function () {
            let whoAmI = localStorage.lastLoggedInUser;
            if (!whoAmI) {
                MessageToast.show("Kullanıcı bilgisi alınamadı.");
                whoAmI = "TV_USER";
            }
            const selectedNCsModel = this.getView().getModel("selectedNCsModel");
            const selectedNCs = selectedNCsModel.getProperty("/items");
            var resource = localStorage.selectedResource.split("-")[0].split(",")[1];
            var request = {
                site: this.site,
                resource: resource,
                sfc: this.podHDRData.SFC,
                user: whoAmI,
                ncCodes: selectedNCs
            };
            var inputJSONModel = new JSONModel();
            inputJSONModel.setData(request);
            var newElemJSON = inputJSONModel.getJSON();
            var xhttpLogNcsForSfc = Utils.xhttpPost(
                "/bekorest/restapi/qualityChainController/testNOK?site=" + this.site, newElemJSON);
            if (JSON.parse(xhttpLogNcsForSfc.response).success) {
                this.changeInfoText(JSON.parse(xhttpLogNcsForSfc.response).messageCode, "Accept");
            } else {
                this.changeInfoText(JSON.parse(xhttpLogNcsForSfc.response).messageCode, "Reject");
            }
            const ncsToLog = selectedNCs.filter(nc => nc.ncWillLog && !nc.repaired);
            const repairsToLog = selectedNCs.filter(nc => nc.repairWillLog);
            MessageToast.show(this.getView().getModel("i18n").getResourceBundle().getText("ncAndRepairSaved.label") + `${ncsToLog.length} NC - ${repairsToLog.length}` + this.getView().getModel("i18n").getResourceBundle().getText("repair.label"));
            // Close the dialog
            this.onCloseNCDialog();
        },
        onPressReprintSFC: function (oEvent) {
            var oView = this.getView();
            var oDialog = oView.byId("idCreateBarcodeForPrintDialog");
            if (!oDialog) {
                oDialog = sap.ui.xmlfragment(oView.getId(),
                    "production.fragments.createBarcodeForPrint", this
                );
                oView.addDependent(oDialog);
                /*oDialog.bindElement({
                    path: oContext.getPath(),
                    model: "ShopOrdersModel"
                });*/
            }
            let params = {
                site: this.site,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
                resource: localStorage.selectedResource.split("-")[0].split(",")[1]
            }
            var endPoint = "/panelPreparationController/findReprintSFCLabel";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl);
            oDialog.open();
            let data = JSON.parse(callRequest.response)
            if (data.errorCode) {
                this.changeInfoText(JSON.parse(callRequest.response).messageCode, "Reject");
                return;
            }
            else if (data.sfc) {
                this.byId("idSFCForBarcodePrint").setValue(data.sfc);
                this.byId("idItemCodeForBarcodePrint").setValue(data.item);
                this.byId("idItemDescForBarcodePrint").setValue(data.itemDesc);
            }

        },
        onPressSendBarcodeForPrintDialog: function () {
            let selectedSfc = this.byId("idSFCForBarcodePrint").getValue();
            let params = {
                site: this.site,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "en",
                sfc: selectedSfc,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                type: "PACKAGE"
            }
            var endPoint = "/panelPreparationController/reprintSFCLabel";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpPost(buildUrl);
            this.getView().byId("idCreateBarcodeForPrintDialog").destroy();
            var response = JSON.parse(callRequest.response);
            if (response.success) {
                this.changeInfoText(response.messageCode, "Accept");
            }
            else {
                this.changeInfoText(response.messageCode, "Reject");
            }
        },

        closeBarcodeForPrintDialog: function () {
            this.getView().byId("idCreateBarcodeForPrintDialog").destroy();
        },
    });
}); 