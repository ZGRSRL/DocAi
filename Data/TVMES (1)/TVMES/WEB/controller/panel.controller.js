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
    var site;
    return BaseController.extend("production.controller.panel", {
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
            if (onScan.isAttachedTo(document)) {
                onScan.detachFrom(document);
            }
            this.site = this.getPlant();
            this.appView = this.getOwnerComponent().getRootControl();
            this.appWorkCenter = this.appView.byId("idWorkcenterCombo");
            this.appResource = this.appView.byId("idResrceCombo");
            this.appRefresh = this.appView.byId("idRefresh");
            this.appLanguage = this.appView.byId("idLanguageCombo");

            this.appRefresh.attachPress(this.getActiveSFCInformation.bind(this));
            this.appRefresh.attachPress(this.connectWebSocket.bind(this));
            this.appResource.attachChange(this.getActiveSFCInformation.bind(this));
            this.appResource.attachChange(this.connectWebSocket.bind(this));
            this.appLanguage.attachChange(this.getActiveSFCInformation.bind(this));

            localStorage.selectedLanguage = this.appLanguage.getSelectedKey();
            var selectedResource = localStorage.selectedResource;
            localStorage.resourceType = "PANEL";
            var oParameters = oEvent.getParameters();
            this.connectWebSocket();
            this.loadShopOrders();
            if (localStorage.refreshInterval) {
                clearInterval(localStorage.refreshInterval);
            }
            localStorage.refreshInterval = setInterval(this.refreshActiveTableData.bind(this), 1200000);

            let options = {
                timeBeforeScanTest: 100,
                avgTimeByChar: 50,
                minLength: 6,
                suffixKeyCodes: "",
                prefixKeyCodes: "",
                scanButtonLongPressTime: 500,
                stopPropagation: false,
                preventDefault: false,
                reactToPaste: true,
                reactToKeyDown: true,
                singleScanQty: 1
            }

            if (!onScan.isAttachedTo(document)) {
                options.onScan = function (barcode, qty) {
                    this.barcodeFnRouterBarcode(barcode);
                }.bind(this);
                onScan.attachTo(document, options);
            }
        },

        barcodeFnRouterBarcode: function (barcode) {

            if (this.appView.byId("idOperatorLoginDialog") && this.appView.byId("idOperatorLoginDialog").isOpen()) {
                this.operatorLoginRequest(barcode);
                return null;
            }

        },
        //-----------------------------------------------------------------------------//
        // Shop Order Details 
        //-----------------------------------------------------------------------------//
        // Handle login button press
        onPressNCDialogLogin: function () {
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
                    try {
                        var response = JSON.parse(request.responseText);
                        if (response.FORM_ID) {
                            let xHttpLoginUser = Utils.xhttpPost("/bekorest/restapi/qualityChainController/loginUser?site="
                                + this.site + "&user=" + sUsername, {});
                            if (JSON.parse(xHttpLoginUser.response).success) {
                                this._oNCLoginDialog.close();
                                this.onPressReprintSFC();
                            } else {
                                MessageToast.show("Kullanıcıya izin verilmedi.");
                                return;
                            }

                        } else {
                            MessageToast.show("Kullanıcı adı/ Şifre yanlış");
                            return;
                        }
                    } catch (e) {
                        MessageToast.show("NC Login failed: " + e);
                    }
                }
            } else {
                MessageToast.show("Please enter both username and password");
            }
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
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
                sfc: selectedSfc,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                type: "PANEL"
            }
            var endPoint = "/panelPreparationController/reprintSFCLabel";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpPost(buildUrl);
            this.getView().byId("idCreateBarcodeForPrintDialog").destroy();
            var response = JSON.parse(callRequest.response);
            if (response.success) {
                this.getActiveSFCInformation();
                this.changeInfoText(response.messageCode, "Accept");
            }
            else {
                this.getActiveSFCInformation();
                this.changeInfoText(response.messageCode, "Reject");
            }
        },

        closeBarcodeForPrintDialog: function () {
            this.getView().byId("idCreateBarcodeForPrintDialog").destroy();
        },

        //-----------------------------------------------------------------------------//
        // Start & Close Shop Order
        //-----------------------------------------------------------------------------//
        onExit: function () {
            appRefresh.detachPress(this.loadShopOrders.bind(this))
            appResource.detachChange(this.loadShopOrders.bind(this));
            appResource.detachChange(this.connectWebSocket.bind(this));
            this.closeConnection();
            this.getRouter().detachRouteMatched(this.onRouteMatched, this);
        },
        onPressStartOrder: function (oEvent) {
            var oSource = oEvent.getSource();
            var oContext = oSource.getBindingContext("ShopOrdersModel");
            var shopOrder = oContext.getObject().shopOrder;

            let params = {
                site: this.site,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
                workCenter: localStorage.selectedWorkCenter,
                shopOrder: shopOrder
            };

            var endPoint = "/panelPreparationController/startShopOrder";
            var buildUrl = Utils.buildUrl(endPoint, params);

            Utils.asyncPOST(buildUrl, function (response) {
                if (response.success) {
                    if (response.messageCode) {
                        this.getActiveSFCInformation();
                        this.changeInfoText(response.messageCode, "Accept");
                    }
                } else {
                    if (response.messageCode) {
                        this.getActiveSFCInformation();
                        this.changeInfoText(response.messageCode, "Reject");
                    }
                }
            }.bind(this));
        },
        onPressStopOrder: function (oEvent) {
            var oSource = oEvent.getSource();
            var oContext = oSource.getBindingContext("ShopOrdersModel");
            var shopOrder = oContext.getObject().shopOrder;
            let params = {
                site: this.site,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
                workCenter: localStorage.selectedWorkCenter,
                shopOrder: shopOrder,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                operation: localStorage.selectedResource.split("-")[2].split(",")[1]
            };

            var endPoint = "/panelPreparationController/holdShopOrder";
            var buildUrl = Utils.buildUrl(endPoint, params);

            Utils.asyncPOST(buildUrl, function (response) {
                if (response.success) {
                    if (response.messageCode) {
                        this.getActiveSFCInformation();
                        this.changeInfoText(response.messageCode, "Accept");
                    }

                } else {
                    if (response.messageCode) {
                        this.getActiveSFCInformation();
                        this.changeInfoText(response.messageCode, "Reject");
                    }
                }
            }.bind(this));
        },
        onPressHoldProduct: function (oEvent) {
            let params = {
                site: this.site,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
                workCenter: localStorage.selectedWorkCenter,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                operation: localStorage.selectedResource.split("-")[2].split(",")[1]
            };

            var endPoint = "/panelPreparationController/holdProduct";
            var buildUrl = Utils.buildUrl(endPoint, params);

            Utils.asyncPOST(buildUrl, function (response) {
                if (response.success) {
                    if (response.messageCode) {
                        this.getActiveSFCInformation();
                        this.changeInfoText(response.messageCode, "Accept");
                    }
                } else {
                    if (response.messageCode) {
                        this.getActiveSFCInformation();
                        this.changeInfoText(response.messageCode, "Reject");
                    }
                }
            }.bind(this));
        },
        onPressCompleteSFC: function (oEvent) {
            let params = {
                site: this.site,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
                resource: localStorage.selectedResource.split("-")[0].split(",")[1],
                test: true,
                printerIP: "10.88.128.13"
            };
            let hostname = window.location.origin.split("//")[1];
            if (hostname == 'sbldhk20v.ar.arcelik:50000') {
                params.test = true;
                params.printerIP = "127.0.0.1";
            }
            var endPoint = "/panelPreparationController/completeSFCPanel";
            var buildUrl = Utils.buildUrl(endPoint, params);

            Utils.asyncPOST(buildUrl, function (response) {
                if (response.success) {
                    if (response.messageCode) {
                        this.changeInfoText(response.messageCode, "Accept");
                    }
                    this.getActiveSFCInformation();
                } else {
                    if (response.messageCode) {
                        this.changeInfoText(response.messageCode, "Reject");
                        this.getActiveSFCInformation();
                    }
                }
            }.bind(this));
        },
        onPressNewSFC: function (oEvent) {
            let params = {
                site: this.site,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr",
                workCenter: localStorage.selectedWorkCenter,
                resource: localStorage.selectedResource.split("-")[0].split(",")[1]
            };

            var endPoint = "/panelPreparationController/startSFCPanel";
            var buildUrl = Utils.buildUrl(endPoint, params);

            Utils.asyncPOST(buildUrl, function (response) {
                if (response.success) {
                    if (response.messageCode) {
                        this.changeInfoText(response.messageCode, "Accept");
                    }
                    this.getActiveSFCInformation();
                } else {
                    if (response.messageCode) {
                        this.changeInfoText(response.messageCode, "Reject");
                        this.getActiveSFCInformation();
                    }
                }
            }.bind(this));
        },
    })
});
