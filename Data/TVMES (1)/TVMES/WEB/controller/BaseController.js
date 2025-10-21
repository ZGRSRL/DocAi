sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/core/routing/History",
    "sap/ui/core/UIComponent",
    "../scripts/customStyle",
    "../scripts/custom",
    "production/scripts/Utils",
    "sap/m/MessageBox",
    "sap/m/Popover",
    "sap/m/Dialog",
    "sap/m/DialogType",
    "sap/m/Label",
    "sap/m/LabelDesign",
    "sap/m/Input",
    "sap/m/MessageToast",
    "sap/m/FormattedText",
    "sap/m/VBox",
    "sap/m/HBox",
    "sap/m/Button",
    "sap/m/ButtonType",
    "sap/ui/model/json/JSONModel",
    "production/scripts/WebSocketManager",
    "production/scripts/MQTTManager",
    "production/scripts/ButtonTypeWarning"
], function (Controller, History, UIComponent, customStyle, custom, Utils, MessageBox, Popover, Dialog, DialogType, Label, LabelDesign, Input, MessageToast, FormattedText, VBox, HBox, Button, ButtonType, JSONModel, WebSocket, MQTTManager, ButtonTypeWarning) {
    "use strict";
    var currentResource;
    var generalInfoMessageComp;
    var notificationMessageComp;
    var cabinetController;
    var openWsArray = [];
    var client;
    var refreshMQTTInterval;
    var connectionCheckMS = 10000;
    var appView;
    var canBeScroll;
    var keepAliveInterval;
    var oOperatorLoginDialog;
    var inputOrder;
    return Controller.extend("production.controller.BaseController", {
        onInit: function () {
        },
        getPlant: function () {
            return "6423";
        },
        setSelectedResource: function (oResource) {
            this.currentResource = oResource;
        },
        keepAliveSession: function () {
            var uri = "/XMII/Illuminator?service=admin&mode=Who&content-type=text/json";
            Utils.asyncGET(uri, this.keepAliveCallback.bind(this));
        },
        keepAliveCallback: function () {
            //Keep Alive
        },
        connectWebSocket: function () {
            let mqttUrl = "sbldhk20v", mqttPort = 8190, useSSLParam = false;
            let hostname = window.location.origin.split("//")[1];
            if (hostname == 'sbldhk29v.ar.arcelik:50000' || hostname == 'sbldhk29v.ar.arcelik:50000' || hostname == 'sblmes.arcelik.com') {
                mqttUrl = "sbldhk29v.ar.arcelik"; mqttPort = 8190;
                if (hostname == 'sblmes.arcelik.com') {
                    useSSLParam = true; mqttPort = 8194; mqttUrl = "sbldhk29v.ar.arcelik";
                }
            }
            if (!this.keepAliveInterval)
                this.keepAliveInterval = setInterval(this.keepAliveSession.bind(this), 120000);
            this.appView = sap.ui.core.Component.getOwnerComponentFor(this.getView()).getRootControl();
            if (!this.refreshMQTTInterval) {
                clearInterval(this.refreshMQTTInterval);
                this.refreshMQTTInterval = setInterval(function () {
                    if (this.client) {
                        if (!this.client.isConnected())
                            this.connectWebSocket();
                    }
                }.bind(this), 20000);
            }
            let resource = localStorage.selectedResource.split("-")[1];
            let resourceType = localStorage.selectedResource.split("-")[3];
            let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
            if (this.client) {
                if (this.client.isConnected())
                    this.client.disconnect();
            }

            if (useSSLParam == true) {
                let fullMqttUrl = "wss://" + mqttUrl + ":" + Number(mqttPort) + "/mqtt";
                this.client = new Paho.MQTT.Client(fullMqttUrl, resource + "_POD" + uuid);
            } else {
                this.client = new Paho.MQTT.Client(mqttUrl, Number(mqttPort), resource + "_POD" + uuid);
            }
            // this.client = new Paho.MQTT.Client(mqttUrl, Number(mqttPort), resource + "_POD" + uuid);
            this.client.onMessageArrived = this.handleWebSocketMessage.bind(this);
            this.client.onConnectionLost = function (responseObject) {
                if (responseObject.errorCode !== 0) {
                    console.log("onConnectionLost: " + responseObject.errorMessage);
                    let btn = this.getView().getParent().getParent().byId("connect");
                    btn.setType("Reject");
                    btn.setIcon("sap-icon://disconnected");
                }
            }.bind(this);
            let connectOpts = {
                useSSL: useSSLParam,
                onSuccess: function () {
                    console.log("onConnect: " + resource);
                    this.client.subscribe(localStorage.selectedWorkCenter + "/ShopOrders");
                    let btn = this.getView().getParent().getParent().byId("connect");
                    btn.setType("Accept");
                    btn.setIcon("sap-icon://connected");
                }.bind(this)
            };
            if (useSSLParam == true) {
                connectOpts = {
                    useSSL: useSSLParam,
                    onSuccess: function () {
                        console.log("onConnect: " + resource);
                        this.client.subscribe(localStorage.selectedWorkCenter + "/ShopOrders");
                        let btn = this.getView().getParent().getParent().byId("connect");
                        btn.setType("Accept");
                        btn.setIcon("sap-icon://connected");
                    }.bind(this)
                };
            }
            this.client.connect(connectOpts);

        },
        traceFn: function (data) {
            console.log(data);
        },
        setInputOrder: function (inputOrder) {
            this.inputOrder = inputOrder;
        },
        setGeneralInfoMessageComp: function (oComp) {
            this.generalInfoMessageComp = oComp;
        },
        setNotificationMessageComp: function (oComp) {
            this._oNotificationMessageComp = oComp;
        },
        getNotificationMessageComp: function () {
            return this._oNotificationMessageComp;
        },
        showNotificationMessage: function (sMessage, sType) {
            var oNotificationMessageComp = this.getNotificationMessageComp();
            if (oNotificationMessageComp) {
                oNotificationMessageComp.setType(sType);
                oNotificationMessageComp.setText(sMessage);
                oNotificationMessageComp.setVisible(true);
            }
        },
        showSuccessMessage: function (sMessageCode) {
            var sMessage = this.getResourceBundle().getText(sMessageCode);
            this.showNotificationMessage(sMessage, "Accept");
        },
        showErrorMessage: function (sMessageCode) {
            var sMessage = this.getResourceBundle().getText(sMessageCode);
            let errorCode = sMessage.split(".")[0];
            this.showNotificationMessage(sMessage + " (" + errorCode + ")", "Reject");
        },
        changeInfoText: function (text, type) {
            this.messageData.infoMessage = text;
            this.messageData.infoMessageType = type;
            this.getView().getModel("messageModel").refresh(true);
        },
        changeNotifText: function (text, type) {
            this.messageData.notificationMessage = text;
            this.messageData.notificationMessageType = type;
            this.getView().getModel("messageModel").refresh(true);
        },
        changeTestButton: function (sfc) {
            let testButton = this.getView().byId("testNOKButton");
            if (!testButton) return;
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
        getRouter: function () {
            return UIComponent.getRouterFor(this);
        },
        handleWebSocketMessage: function (data) {
            let message = JSON.parse(data.payloadString);
            if (message.shopOrderDTO) {
                if (message.shopOrderDTO.length < 1) return;
                let dataS = message.shopOrderDTO.filter(x => x.resource == localStorage.selectedResource.split("-")[1])[0]
                console.log(dataS)
                if (dataS)
                    this.loadShopOrdersCallBack(dataS);
            }
            if (message.notificationMessageData) {
                var msgData = message.notificationMessageData;
                if (msgData.messageType && msgData.messageCode) {
                    var i18nText = msgData.messageType + "_" + msgData.messageCode;
                    var bundled = this.getView().getModel("i18n").getResourceBundle().getText(i18nText);
                    var messageType = bundled.split(":")[0] == "E" ? "Reject" : bundled.split(":") == "W" ? "Transparent" : "Accept";
                    var messageText = bundled.split(":")[1];
                    if (messageText == undefined) messageText = bundled;
                    this.changeInfoText(messageText, messageType);
                    if (message.notificationMessageData.messageAction) {
                        if (message.notificationMessageData.messageAction == "REFRESH_SFC_INFO" && message.notificationMessageData.sfc) {
                            this.getActiveSFCInformation();
                            if (this.getView().byId("idIconTabBar").getSelectedKey() == "barcodeSFCList") {
                                this.loadBarcodeSFCList();
                            }
                            if (this.getView().byId("idIconTabBar").getSelectedKey() == "MaterialList")
                                this.loadMaterialList();
                        }
                    }
                }
                else {
                    this.changeInfoText("", "Accept");
                    this.changeNotifText("", "Accept");
                }
                if (msgData.sfc || msgData.palletID) {
                    if (!this.podHDRData) this.refreshPODHDRData();
                    if (msgData.sfc) {
                        this.podHDRData.SFC = msgData.sfc;
                    }
                    if (msgData.palletID) {
                        this.podHDRData.PALLET_NO = msgData.palletID;
                    }
                    this.refreshPODHDRData();
                }

            }
            if (message.infoMessageData) {
                var messageText = message.infoMessageData.message;
                var messageType = message.infoMessageData.messageCode;
                this.changeNotifText(messageText, messageType);
                if (message.infoMessageData.messageAction) {
                    if (message.infoMessageData.messageAction == "REFRESH_SFC_INFO" && message.infoMessageData.sfc) {
                        this.getActiveSFCInformation();
                    }
                    if (message.infoMessageData.messageAction == "REFRESH_MATERIAL_LIST") {
                        if (this.getView().byId("idIconTabBar").getSelectedKey() == "MaterialList")
                            this.loadMaterialList();
                    }
                }
            }

        },
        refreshActiveTableData: function () {
            this.loadShopOrders();
        },
        getActiveSFCInformation: function () {
            var endPoint = "/UIComponentsController/getActiveShopOrderInfo";
            var params = {
                site: this.getPlant(),
                locale: "en",
                resource: localStorage.selectedResource.split("-")[1],
                workCenter: localStorage.selectedWorkCenter,
                operation: localStorage.selectedResource.split("-")[2].split(",")[1],
                logDuration: true
            }
            var buildUrl = Utils.buildUrl(endPoint, params);
            Utils.asyncGET(buildUrl, this.getActiveSFCInformationCallback.bind(this));
        },
        getActiveSFCInformationCallback: function (data) {
            if (!data.item)
                this.podHDRData = {
                    ITEM: "-",
                    ITEM_DESCRIPTION: "-",
                    SHOP_ORDER: "-",
                    PLANNED_QUAN: "-",
                    THIS_STATION_COMPLETED: "-",
                    THIS_STATION_REMAINING: "-",
                    SFC: "",
                    TEST_OK: null
                };
            else {
                this.podHDRData = {
                    ITEM: data.item.split(",")[1],
                    ITEM_DESCRIPTION: data.description,
                    SHOP_ORDER: data.shopOrder.split(",")[1],
                    PLANNED_QUAN: data.plannedQty,
                    THIS_STATION_COMPLETED: data.producedQty,
                    THIS_STATION_REMAINING: data.remainingQty,
                    SFC: data.activeSfc ? data.activeSfc.split(",")[1] : "",
                    TEST_OK: data.testOK

                };
                this.changeTestButton(this.podHDRData.SFC);
            }
            if (!this.podHDRData) {
                this.podHDRData = {
                    ITEM: "-",
                    ITEM_DESCRIPTION: "-",
                    SHOP_ORDER: "-",
                    SFC: "",
                    PLANNED_QUAN: "-",
                    THIS_STATION_COMPLETED: "-",
                    THIS_STATION_REMAINING: "-",
                    TEST_OK: null
                };
            }
            var oModel = this.getView().getModel("podHDRModel")
            if (!oModel) {
                oModel = new JSONModel();
                oModel.setData(this.podHDRData);
                this.getView().setModel(oModel, "podHDRModel");

            } else {
                oModel.setData(this.podHDRData);
                oModel.refresh();
            }
            if (this.byId("sfcInput")) {
                if (this.byId("sfcInput").getValue().length > 0) {
                    if (this.inputOrder && this.inputOrder.length > 0) {
                        this.checkFocusOrder(this.inputOrder);
                    }
                }
                if (this.podHDRData && this.podHDRData.SFC != "") {
                    if (this.inputOrder && this.inputOrder.length > 0) {
                        this.checkFocusOrder(this.inputOrder);
                    }
                }
                else {
                    this.byId("sfcInput").setValue("");
                    this.setFocusWithId("sfcInput");
                }
            }
        },
        refreshPODHDRData: function () {
            if (!this.podHDRData) {
                this.podHDRData = {
                    ITEM: "-",
                    ITEM_DESCRIPTION: "-",
                    SHOP_ORDER: "-",
                    SFC: "",
                    PLANNED_QUAN: "-",
                    THIS_STATION_COMPLETED: "-",
                    THIS_STATION_REMAINING: "-",
                };
            }

            if (!this.podHDRModel)
                this.podHDRModel = new JSONModel();
            this.podHDRModel.setData(this.podHDRData);
            this.getView().setModel(this.podHDRModel, "podHDRModel");
            localStorage.POD_HDR_DATA = JSON.stringify(this.podHDRData);
        },
        onNavBack: function () {
            var oHistory, sPreviousHash;
            oHistory = History.getInstance();
            sPreviousHash = oHistory.getPreviousHash();

            if (sPreviousHash !== undefined) {
                window.history.go(-1);
            } else {
                this.getRouter().navTo("appHome", {}, true /*no history*/);
            }
        },
        loadWorkCenters: function () {
            var endPoint = "/UIComponentsController/getWorkCenters";
            var params = {
                site: "6423",
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "en"
            }
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl);
            if (callRequest.status !== 200 && callRequest.status !== 204) {
                Utils.showErrorMessage(this.getView().getModel("i18n").getResourceBundle().getText("workcenterInformationNotFound.error.label"))
                return;
            }
            this.workcenterData = JSON.parse(callRequest.responseText).workCenters;
            this.workcenterListModel = new JSONModel();
            this.workcenterListModel.setSizeLimit(10000);
            this.workcenterListModel.setData(this.workcenterData);
            this.getView().setModel(this.workcenterListModel, "WorkcenterModel");
            this.getView().getModel("WorkcenterModel").refresh(true);
            if (window.location.search.split("?")[1]) {
                var params = window.location.search.split("?")[1];
                var workCenterS = params.split("&")[0];
                if (workCenterS) {
                    var workCenter = workCenterS.split("=")[1];
                    var d = this.workcenterData.filter(x => x.workCenter == workCenter)[0];
                    var dIndex = this.workcenterData.findIndex(x => x.workCenter == workCenter);
                    var dItem = this.byId("idResrceCombo").getItems()[dIndex];
                    this.byId("idWorkcenterCombo").setSelectedKey(d.workCenter);
                    this.byId("idWorkcenterCombo").setSelectedItem(dItem);
                    localStorage.selectedWorkCenter = this.byId("idWorkcenterCombo").getSelectedKey();
                    this.byId("idWorkcenterCombo").setValueState("Success");
                    this.byId("idWorkcenterCombo").setEnabled(false);
                }
            }
            if (localStorage.selectedWorkCenter) {
                this.byId("idWorkcenterCombo").setSelectedKey(localStorage.selectedWorkCenter);
            }
            else {
                this.byId("idWorkcenterCombo").setSelectedKey(this.workcenterData[0].workCenter);
                localStorage.selectedWorkCenter = this.byId("idWorkcenterCombo").getSelectedKey();

            }

            this.loadResources(localStorage.selectedWorkCenter);
        },
        onChangeWorkcenter: function () {
            localStorage.selectedWorkCenter = this.byId("idWorkcenterCombo").getSelectedKey();
            this.loadResources(localStorage.selectedWorkCenter);
        },
        loadResources: function (selectedWorkCenter) {
            if (this.resourceListModel) this.resourceListModel.setData([]);
            var endPoint = "/UIComponentsController/getResources";
            var params = {
                site: "6423",
                workCenter: selectedWorkCenter,
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "en"
            }
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl);
            if (callRequest.status !== 200 && callRequest.status !== 204) {
                this.changeNotifText(this.getView().getModel("i18n").getResourceBundle().getText("resourceInformationNotFound.error.label"))
                return;
            }
            if (!JSON.parse(callRequest.responseText).resources) {
                this.changeNotifText(this.getView().getModel("i18n").getResourceBundle().getText("resourceInformationNotFound.error.label"))
                return;
            }
            this.resourceData = JSON.parse(callRequest.responseText).resources;
            this.resourceListModel = new JSONModel();
            this.resourceListModel.setSizeLimit(10000);
            this.resourceListModel.setData(this.resourceData);
            this.getView().setModel(this.resourceListModel, "ResrceModel");
            this.getView().getModel("ResrceModel").refresh(true);
            if (window.location.search.split("?")[1]) {
                var params = window.location.search.split("?")[1];
                if (params) {
                    var resourceS = params.split("&")[1];
                    if (resourceS) {
                        var resource = resourceS.split("=")[1];
                        var d = this.resourceData.filter(x => x.resource == resource)[0];
                        var dIndex = this.resourceData.findIndex(x => x.resource == resource);
                        var dItem = this.byId("idResrceCombo").getItems()[dIndex];
                        this.byId("idResrceCombo").setSelectedKey(d.handle + "-" + d.resource + "-" + d.operationRef + "-" + d.resourceType);
                        this.byId("idResrceCombo").setSelectedItem(dItem);
                        localStorage.selectedResource = this.byId("idResrceCombo").getSelectedKey();
                        this.byId("idResrceCombo").setValueState("Success");
                        this.byId("idResrceCombo").setEnabled(false);
                    }
                }
            } else {
                this.byId("idResrceCombo").setSelectedKey(this.resourceData[0].resourceRef + "-" + this.resourceData[0].resource + "-" + this.resourceData[0].operationBo + "-" + this.resourceData[0].resourceType);
                localStorage.selectedResource = this.byId("idResrceCombo").getSelectedKey();
                this.loadShopOrders();
            }


        },
        onChangeResource: function () {
            localStorage.selectedResource = this.byId("idResrceCombo").getSelectedKey();
            this.loadShopOrders();
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
        loadShopOrders: function () {
            return;
            this.canBeScroll = true;
            let operationBo = localStorage.selectedResource.split("-")[2];
            let params = {
                site: this.getPlant(),
                workCenter: localStorage.selectedWorkCenter,
                operation: operationBo.split(",")[1],
                locale: localStorage.selectedLanguage ? localStorage.selectedLanguage : "tr"
            }
            var endPoint = "/UIComponentsController/getShopOrders";
            var buildUrl = Utils.buildUrl(endPoint, params);
            Utils.asyncGET(buildUrl, this.loadShopOrdersCallBack.bind(this));
        },
        loadShopOrdersCallBack: function (data) {
            if (!data.shopOrders && !data.shopOrderDTO[0].shopOrders) {
                if (this.shopOrderListModel)
                    this.shopOrderListModel.setData({});
                this.changeNotifText("Sipariş bilgileri bulunamadı.", "Reject");
                return;
            }
            if (data.shopOrders)
                this.shopOrderListData = data.shopOrders;
            else if (data.shopOrderDTO[0].shopOrders)
                this.shopOrderListData = this.shopOrderListData = data.shopOrderDTO[0].shopOrders;
            else return;
            /* ShopOrder Button Enable/Disable*/
            if (this.shopOrderListData.filter(x => x.status == "ACTIVE").length > 0) {
                this.shopOrderListData.filter(x => x.status != "ACTIVE").map(x => x.shopOrderButtonEnabled = false);
            }
            this.shopOrderListData = this.shopOrderListData.map(order => {
                const itemParts = order.item.split(",");
                return {
                    ...order, // Diğer özellikleri koru
                    item: itemParts[1] !== undefined ? itemParts[1].replace(/^0+/, '') : order.item
                };
            });
            this.shopOrderListModel = new JSONModel();
            this.shopOrderListModel.setSizeLimit(10000);
            this.shopOrderListModel.setData(this.shopOrderListData);
            this.getView().setModel(this.shopOrderListModel, "ShopOrdersModel");
            this.getView().getModel("ShopOrdersModel").refresh(true);
            this.setRowColorForShopOrdersTab(this.shopOrderListData.length, this.shopOrderListData);
            this.waitAndScrollToActiveRow(this);
            //PodHDR Model
            if (!this.podHDRData)
                this.podHDRData = {
                    ITEM: "-",
                    ITEM_DESCRIPTION: "-",
                    SHOP_ORDER: "-",
                    SFC: "",
                    PLANNED_QUAN: "-",
                    THIS_STATION_COMPLETED: "-",
                    THIS_STATION_REMAINING: "-",
                };
        },

        loadMaterialList: function () {
            let params = {
                site: "BMI",
                sfc: this.podHDRData.SFC,
                resource: localStorage.selectedResource.split("-")[1]
            }
            let resourceType = localStorage.selectedResource.split("-")[3];
            var endPoint = "/traceabilityController/getMaterialList";
            var buildUrl = Utils.buildUrl(endPoint, params);
            Utils.asyncGET(buildUrl, this.loadMaterialListCallback.bind(this));

        },
        loadMaterialListCallback: function (data) {

            if (!data.componentMembers) {
                if (this.MaterialListModel)
                    this.MaterialListModel.setData({});
                return;
            }
            this.materialListData = data.componentMembers;
            this.materialListData = this.materialListData.map(o => {
                const itemParts = o.componentCode.split(",");
                return {
                    ...o, // Diğer özellikleri koru
                    componentCode: itemParts[1] !== undefined ? itemParts[1].replace(/^0+/, '') : o.componentCode
                };
            });
            this.MaterialListModel = new JSONModel();
            this.MaterialListModel.setSizeLimit(10000);
            this.MaterialListModel.setData(this.materialListData);
            this.getView().setModel(this.MaterialListModel, "MaterialListModel");
            this.getView().getModel("MaterialListModel").refresh(true);
            this.setRowColorForMaterialListTab(this.materialListData.length, this.materialListData);
        },

        onPressCloseAdministrationFieldsDialog: function () {
            this.getView().byId("idAdministrationFieldsDialog").destroy();
        },

        onPressDisassemble: function (oEvent) {
            if (oEvent.oSource.mProperties.type == "Accept") {
                this.pressedCompButtonId = oEvent.oSource.sId
                var deleteMessageTitle = this.getView().getModel("i18n").getResourceBundle().getText("OEE_LABEL_DISASSY_COMPONENT_TITLE");
                var deleteMessageText = this.getView().getModel("i18n").getResourceBundle().getText("OEE_LABEL_DISASSY_COMPONENT_MESSAGE");
                this.selectedRowIndexForDisassamble = oEvent.getSource().getBindingContext("MaterialListModel").getPath().split("/")[1];
                MessageBox.confirm(
                    deleteMessageText,
                    function (oResult) {
                        if (oResult == "OK") this.disassembleComponent();
                        else {
                            return;
                        }
                    }.bind(this),
                    deleteMessageTitle
                );
            }
        },
        disassembleComponent: function (p_that) {
            var selectedRow = this.byId(this.pressedCompButtonId).getParent().getBindingContext("MaterialListModel").getModel().getData()[this.selectedRowIndexForDisassamble];
            var selectedSfc = this.podHDRData.SFC;
            var selectedItemBo = selectedRow.componentCode;
            var selectedBarcode = selectedRow.barcode;
            var selectedResource = localStorage.selectedResource.split("-")[1];
            var params = {
                resource: selectedResource,
                site: "BMI",
                barcode: selectedBarcode,
                sfc: selectedSfc,
                item: selectedItemBo
            };
            var endPoint = "/traceabilityController/disassembleComponents";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpPost(buildUrl, JSON.stringify(params));
            this.loadMaterialList();
        },

        assemblyComponent: function (oEvent) {
            var status = this.getView().byId("idMaterialListModel").getHeaderToolbar().getVisible();
            if (status)
                this.getView().byId("idMaterialListModel").getHeaderToolbar().setVisible(false);
            else {
                this.getView().byId("idMaterialListModel").getHeaderToolbar().setVisible(true);
            }
        },
        assembleComponent: function () {
            if (this.getView().byId("idAssyBarcodeComponent").getValue() == "")
                return;
            var selectedBarcode = this.getView().byId("idAssyBarcodeComponent").getValue();
            var selectedResource = localStorage.selectedResource.split("-")[1];
            var params = {
                resource: selectedResource,
                site: "BMI",
                barcode: selectedBarcode
            };
            var endPoint = "/traceabilityController/assembleComponents";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpPost(buildUrl, JSON.stringify(params));
            this.loadMaterialList();
            if (callRequest.status !== 200 && callRequest.status !== 204) {
                Utils.showErrorMessage("İşlem başarısız.")
                return;
            }
            this.getView().byId("idAssyBarcodeComponent").setValue("");

        },

        onPressLogComponentNc: function () {
            var oView = this.getView(),
                oDialog = oView.byId("idLogNonconformanceDialog");
            var params = {
                site: "BMI"
            };
            var endPoint = "/nonConformanceController/getNcGroups";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl, JSON.stringify(params));
            var ncList = JSON.parse(callRequest.response);
            var componentNcListModel = new JSONModel();
            componentNcListModel.setSizeLimit(10000);
            componentNcListModel.setData(ncList);
            oView.setModel(componentNcListModel,
                "componentNcListModel");

            if (!oDialog) {
                oDialog = sap.ui.xmlfragment(
                    oView.getId(),
                    "production.fragments.logNonconformance",
                    this
                );
                oView.addDependent(oDialog);
            }
            oDialog.open();
        },
        closeEntryNCDialog: function (oEvent) {
            this.getView().byId("idLogNonconformanceDialog").destroy();
        },
        onPressGetNcCodesByGroup: function (oEvent) {
            var oView = this.getView(),
                ncGroup = oEvent.getSource().getBindingContext("componentNcListModel").getObject().ncGroup;
            var params = {
                site: "BMI",
                ncGroup: ncGroup
            };
            var endPoint = "/nonConformanceController/getNcCodesByGroup";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl, JSON.stringify(params));
            var ncCodeList = JSON.parse(callRequest.response);
            var componentNcCodeListModel = new JSONModel();
            componentNcCodeListModel.setSizeLimit(10000);
            componentNcCodeListModel.setData(ncCodeList);
            oView.setModel(componentNcCodeListModel,
                "componentNcCodeListModel");
            oView.byId("idNCListTable").getModel("componentNcCodeListModel").refresh();
        },

        setRowColorForMaterialListTab: async function (lenModel, oData) {
            await new Promise(function (resolve) { setTimeout(resolve, 1) });
            for (var i = 0; i < lenModel; i++) {
                var oRow = oData[i];
                if (this.byId("idMaterialListModel")) return;
                var elementId = this.byId("idMaterialListModel").getItems()[i].sId
                if (oRow.type == 'ASSEMBLED_BOM' || oRow.type == 'ALTERNATIVE_ASSEMBLED_BOM') {
                    document.getElementById(elementId).className = "activeRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
                else if (oRow.type == 'NON_BOM') {
                    document.getElementById(elementId).className = "holdedRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
                else if (oRow.type == 'BOM') {
                    document.getElementById(elementId).className = "completeRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
                else if (oRow.type == 'ALTERNATIVE_BOM')
                    document.getElementById(elementId).className = "alternativeRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                else {
                    document.getElementById(elementId).className = "rowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
            };
        },
        setRowColorForShopOrdersTab: async function (lenModel, oData) {
            await new Promise(function (resolve) { setTimeout(resolve, 500) });
            try {
               for (var i = 0; i < lenModel; i++) {
                var oRow = oData[i];
                if (!this.byId("idShopOrdersModel")) return;
                var elementId = this.byId("idShopOrdersModel").getItems()[i].sId
                if (oRow.remainingCabinetQty == "0" && oRow.status != 'ACTIVE') {
                    document.getElementById(elementId).className = "completeRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                    continue;
                }
                if (oRow.status == 'ACTIVE') {
                    document.getElementById(elementId).className = "activeRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
                else if (oRow.status == 'HOLD') {
                    document.getElementById(elementId).className = "holdedRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
                else if (oRow.status == 'COMPLETE') {
                    document.getElementById(elementId).className = "completeRowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
                else {
                    document.getElementById(elementId).className = "rowColor sapMLIB sapMLIB-CTX sapMLIBShowSeparator sapMLIBTypeInactive sapMLIBFocusable sapMListTblRow"
                }
            };
            } catch (error) {
                
            }


        },

        onPressPrintLabel: function (oEvent) {
            var tableIndex = oEvent.oSource.sId.split("idLastSfcListModel-")[1]
            if (tableIndex) {
                var oRow = this.getView().getModel("barcodeSfcListModel").getData()[tableIndex];
            }
            else {
                var oRow = this.getView().getModel("podHDRModel").getData();
                tableIndex = 0
            }


            var oView = this.getView();
            var oDialog = oView.byId("idCreateBarcodeForPrintDialog");
            if (!oDialog) {
                oDialog = sap.ui.xmlfragment(
                    oView.getId(),
                    "production.fragments.createBarcodeForPrint",
                    this
                );
                oView.addDependent(oDialog);
            }
            oDialog.open();
            if (oRow) {
                this.byId("idModelNoForBarcodePrint").setValue(oRow.MANUFACTURER_PRODUCTION_CODE)
                if (oRow.SFC == "-") {
                    this.byId("idSerialNoForBarcodePrint").setValue("");
                    setTimeout(() => { this.getView().byId("idSerialNoForBarcodePrint").focus() }, 500);
                    return;
                }
                this.byId("idSerialNoForBarcodePrint").setValue(oRow.SFC)
            }
        },



        /* -------------- Focus Active Row ---------------- */
        focusToActiveRow: function () {
            var oModel = this.getView().getModel("ShopOrdersModel");
            if (!oModel) return -1;
            var aData = oModel.getData();
            var iActiveItemIndex = aData.findIndex(function (item) {
                return item.status == "ACTIVE";
            });
            if (iActiveItemIndex !== -1) {
                const oTable = this.getView().byId("idShopOrdersModel");
                if (!oTable) return;
                const oListItems = oTable.getItems();
                if (oListItems.length > (iActiveItemIndex + 4)) {
                    iActiveItemIndex += 4;
                }
                else {
                    iActiveItemIndex = oListItems.length - 1;
                }
                const ofirstItem = oListItems[0];
                const oListItem = oListItems[iActiveItemIndex];
                const ofirstItemDomRef = ofirstItem.getDomRef();
                const oListItemDomRef = oListItem.getDomRef();
                if (ofirstItemDomRef && oListItemDomRef) {
                    ofirstItemDomRef.scrollIntoView({ block: 'nearest' });
                    oListItemDomRef.scrollIntoView({ block: 'nearest' });
                    this.canBeScroll = false;
                }
            }

        },
        waitAndScrollToActiveRow: function (p_this) {
            let attempts = 0;
            const maxAttempts = 3;
            const interval = 200;
            function attemptScroll() {
                if (p_this.canBeScroll) {
                    p_this.focusToActiveRow();
                    attempts++;
                    if (attempts < maxAttempts) {
                        setTimeout(attemptScroll, interval);
                    }
                }
            }
            setTimeout(attemptScroll, interval);
        },
        checkFocusOrder: async function (idOrder) {
            await new Promise(function (resolve) { setTimeout(resolve, 200) });
            for (const e of idOrder) {
                var element = this.byId(e);
                if (element.getEnabled() && (element.getValue() == "" || element.getValue() == "-")) {
                    if (element.getValue() == "-") element.setValue("");
                    this.setFocusWithId(e);
                    break;
                }
            }

        },
        setFocusWithId: function (ids) {
            $(`[id*="${ids}"] input`).focus();
        },

        // QualityChain Actions
        /*Repair Open NC Dialog*/
        onPressLogNc: function () {
            // Initialize NC dialog models
            this._initNCModels();
            this.getOwnerComponent().byId("traceabilityView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();
            this.getOwnerComponent().byId("repairView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();
            this.getOwnerComponent().byId("qualityChainView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();
            this.getOwnerComponent().byId("packageLabelView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();

            this.getOwnerComponent().byId("traceabilityView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this.getOwnerComponent().byId("repairView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this.getOwnerComponent().byId("qualityChainView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this.getOwnerComponent().byId("packageLabelView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this._oRepairDialog = undefined;
            // Create and open dialog
            this._oNCDialog = sap.ui.xmlfragment("production.fragments.logNcRepair", this);
            this.getView().addDependent(this._oNCDialog);

            // When Master panel is opened, switch to StretchCompressMode
            sap.ui.getCore().byId("logNcRepairSplitApp").attachAfterMasterOpen(function () {
                this.setMode(sap.m.SplitAppMode.StretchCompressMode);
            });

            // When Master panel is closed, switch back to ShowHideMode
            sap.ui.getCore().byId("logNcRepairSplitApp").attachAfterMasterClose(function () {
                this.setMode(sap.m.SplitAppMode.ShowHideMode);
            });


            this._loadNCGroups();
            this._loadExistingNCData();
            this._oNCDialog.open();
            this._sortTableRows();
            this._colorTableRows();
            const table = sap.ui.getCore().byId("idSelectedNCsTable");
            table.addEventDelegate({
                onAfterRendering: function () {
                    this._sortTableRows();
                    this._colorTableRows();
                }.bind(this)
            });
        },
        /*Repair Open NC Dialog*/
        // QualityChain Open NC Dialog
        onPressTestNOK: function () {
            if (this.podHDRData.SFC == '') {
                this.changeInfoText("20009.error.label", "Reject");
                return;
            }
            if (this.getView().getViewName().split(".")[2] == "packageLabel") {
                let oButton = this.getView().byId("testNOKButton");
                if (oButton.getType() != 'Warning')
                    return;
            }
            // Initialize NC dialog models
            this._initNCModels();
            this.getOwnerComponent().byId("traceabilityView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();
            this.getOwnerComponent().byId("repairView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();
            this.getOwnerComponent().byId("qualityChainView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();
            this.getOwnerComponent().byId("packageLabelView")?.getDependents().filter(x => x.sId = "ncTestDialog")[0]?.destroy();

            this.getOwnerComponent().byId("traceabilityView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this.getOwnerComponent().byId("repairView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this.getOwnerComponent().byId("qualityChainView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this.getOwnerComponent().byId("packageLabelView")?.getDependents().filter(x => x.sId = "repairCodesDialog")[0]?.destroy();
            this._oRepairDialog = undefined;
            // Create and open dialog

            this._oNCDialog = sap.ui.xmlfragment("production.fragments.qualityChainTest", this);
            this.getView().addDependent(this._oNCDialog);

            // When Master panel is opened, switch to StretchCompressMode
            sap.ui.getCore().byId("ncSplitApp").attachAfterMasterOpen(function () {
                this.setMode(sap.m.SplitAppMode.StretchCompressMode);
            });

            // When Master panel is closed, switch back to ShowHideMode
            sap.ui.getCore().byId("ncSplitApp").attachAfterMasterClose(function () {
                this.setMode(sap.m.SplitAppMode.ShowHideMode);
            });


            this._loadNCGroups();
            this._oNCDialog.open();
            this._loadExistingNCData();
            this._sortTableRows();
            this._colorTableRows();
            const table = sap.ui.getCore().byId("idSelectedNCsTable");
            table.addEventDelegate({
                onAfterRendering: function () {
                    this._sortTableRows();
                    this._colorTableRows();
                }.bind(this)
            });
        },
        _sortTableRows: function () {
            const selectedNCsModel = this.getView().getModel("selectedNCsModel");
            const selectedNCs = selectedNCsModel.getProperty("/items");
            selectedNCs.sort((a, b) => {
                return a.sortOrder - b.sortOrder;
            });
            selectedNCsModel.setProperty("/items", selectedNCs);
            selectedNCsModel.refresh();
        },
        _colorTableRows: function () {
            const table = sap.ui.getCore().byId("idSelectedNCsTable");
            const rows = table.getItems();
            const selectedNCsModel = this.getView().getModel("selectedNCsModel");
            const selectedNCs = selectedNCsModel.getProperty("/items");
            selectedNCs.forEach((nc, index) => {
                const row = rows[index];
                row.removeStyleClass("greenRow");
                row.removeStyleClass("turquoiseRow");
                row.removeStyleClass("yellowRow");
                if (nc.repaired) {
                    row.addStyleClass("greenRow");
                    return;
                }
                if (nc.ncWillLog) {
                    row.addStyleClass("turquoiseRow");
                    return;
                }
                if (!nc.ncWillLog && !nc.repairWillLog) {
                    row.addStyleClass("yellowRow");
                    return;
                }
            });
        },


        _initNCModels: function () {
            // Initialize the NC model with current SFC data
            const sfcModel = {
                SFC: this.getView().getModel("podHDRModel") ? this.getView().getModel("podHDRModel").getProperty("/SFC") : "",
                SHOP_ORDER: this.getView().getModel("podHDRModel") ? this.getView().getModel("podHDRModel").getProperty("/SHOP_ORDER") : ""
            };

            // Initialize selected NCs model
            const selectedNCsModel = new JSONModel({
                items: []
            });
            this.getView().setModel(selectedNCsModel, "selectedNCsModel");
            sap.ui.getCore().setModel(selectedNCsModel, "selectedNCCodes");
            // Load existing NC data for current SFC if available

        },

        _loadNCGroups: function () {
            // Simulate loading NC groups
            // In real implementation, this would be fetched from backend
            var locale = this.appLanguage.getSelectedKey(),
                resource = localStorage.selectedResource.split("-")[0].split(",")[1];
            var params = {
                site: "6423",
                resource: resource
            };
            var endPoint = "/ncRepairController/getNcGroupList";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl, JSON.stringify(params));
            var ncList = [];
            try {
                ncList = JSON.parse(callRequest.response);
            } catch (error) {
                console.error("Error parsing NC groups:", error);
                ncList = [];
            }
            const ncGroupsModel = new JSONModel({
                "NCGroups": ncList
            });

            this.getView().setModel(ncGroupsModel, "ncGroupsModel");

            // Set the model to the master list
            const masterList = sap.ui.getCore().byId("masterList");
            if (masterList) {
                masterList.setModel(ncGroupsModel);
            }
        },

        _loadExistingNCData: function () {
            var params = {
                site: "6423",
                workCenter: this.appWorkCenter.getSelectedKey(),
                resource: localStorage.selectedResource.split("-")[0].split(",")[1]
            };
            var endPoint = "/ncRepairController/getLoggedNcsForSfc";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl, JSON.stringify(params));
            var loggedNcList = [];
            try {
                loggedNcList = JSON.parse(callRequest.response);
            } catch (error) {
                console.error("Error parsing NC groups:", error);
                loggedNcList = [];
            }
            if (loggedNcList.length > 0) {
                loggedNcList.map(x => x.repaired ? x.sortOrder = "999" : x.sortOrder = "998");
                loggedNcList.map(x => x.ncWillLog = false);
                const failureLocales = loggedNcList.map(item => item.failureLocale);
              loggedNcList=  loggedNcList.map(item => ({
  ...item,
  comment: item.comment === "---" ? "" : item.comment
}));
                loggedNcList = loggedNcList.filter(x => x.failureLocale == localStorage.selectedLanguage);
                if (loggedNcList.length < 1) {
                    let uniqueFailureLocales = [...new Set(failureLocales)];
                    uniqueFailureLocales = uniqueFailureLocales.map(x => x == "en" ? "English" : x == "tr" ? "Turkish" : "Bengali");
                    MessageToast.show(`Şu anda verileri görüntüleyeceğiniz dil(ler). Dil bakımı yapmanız gerekebilir.: ${uniqueFailureLocales}`);
                }
            }

            const selectedNCsModel = this.getView().getModel("selectedNCsModel");
            selectedNCsModel.setProperty("/items", loggedNcList);
            selectedNCsModel.refresh();
        },
        onNCGroupSelect: function (oEvent) {
            // Get the selected NC group
            const selectedItem = oEvent.getParameter("listItem");
            const context = selectedItem.getBindingContext("ncGroupsModel");
            const ncGroup = context.getProperty("ncGroup");

            // Clear existing tiles
            const flexBox = sap.ui.getCore().byId("ncTypesContainer");
            flexBox.removeAllItems();

            // Load NC codes for this group
            this._loadNCCodesForGroup(ncGroup);

            // Enable the submit button
            sap.ui.getCore().byId("setNCCodesforSFCBtn").setEnabled(true);
        },

        _loadNCCodesForGroup: function (ncGroup) {
            // In real implementation, this would fetch NC codes from backend
            // For this demo, we'll use dummy data based on the group
            let ncCodes = [];
            var params = {
                site: "6423",
                ncGroup: ncGroup
            };
            var endPoint = "/ncRepairController/getFailureNcCodesByGroup";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl, JSON.stringify(params));
            try {
                ncCodes = JSON.parse(callRequest.response);
            } catch (error) {
                console.error("Error parsing NC codes:", error);
                ncCodes = [];
            }
            if (ncCodes.length > 0 && ncCodes.filter(x => x.locale == localStorage.selectedLanguage).length < 1) {
                const ncCodeLocales = ncCodes.map(item => item.locale);
                let uniqueNCCodeLocales = [...new Set(ncCodeLocales)];
                uniqueNCCodeLocales = uniqueNCCodeLocales.map(x => x == "en" ? "English" : x == "tr" ? "Turkish" : "Bengali");
                MessageToast.show(`Şu anda verileri görüntüleyeceğiniz dil(ler). Dil bakımı yapmanız gerekebilir.: ${uniqueNCCodeLocales}`);
            }
            // Create tiles for each NC code
            const flexBox = sap.ui.getCore().byId("ncTypesContainer");
            ncCodes.forEach(ncCode => {
                if (ncCode.locale != localStorage.selectedLanguage) return;
                const tile = new sap.m.GenericTile({
                    header: ncCode.description,
                    subheader: ncCode.ncCode,
                    press: this.onNCTilePress.bind(this)
                }).addStyleClass("sapUiTinyMarginBegin sapUiTinyMarginTop tileWidthHeight");

                // Check if this NC code is already in the selected list and mark it as selected
                const selectedNCsModel = this.getView().getModel("selectedNCsModel");
                const selectedNCs = selectedNCsModel.getProperty("/items");
                if (selectedNCs && selectedNCs.length > 0) {
                    if (selectedNCs.find(item => item.code === ncCode.NcCode)) {
                        tile.addStyleClass("selectedTile");
                    }
                }
                flexBox.addItem(tile);
            });
        },

        onNCTilePress: function (oEvent) {
            const tile = oEvent.getSource();
            const ncCode = tile.getProperty("subheader");
            const ncDescription = tile.getProperty("header");

            const selectedNCsModel = this.getView().getModel("selectedNCsModel");
            if (!selectedNCsModel) {
                selectedNCsModel = new JSONModel({
                    items: []
                });
                this.getView().setModel(selectedNCsModel, "selectedNCsModel");
            }
            if (selectedNCsModel.getProperty("/items") === undefined) {
                selectedNCsModel.setProperty("/items", []);
            }
            const selectedNCs = selectedNCsModel.getProperty("/items");
            // Add to the selected list
            const newNC = {
                rowId: "row_" + Math.random().toString(16).slice(2),
                code: ncCode,
                failureDesc: ncDescription,
                comment: "",
                repaired: false,
                ncCategory: "FAILURE",
                ncWillLog: true,
                repairWillLog: false,
                repairCode: "",
                sortOrder: "0"
            };

            // Check if this NC is already in the selected list

            selectedNCs.push(newNC);
            selectedNCsModel.setProperty("/items", selectedNCs);
            selectedNCsModel.refresh();

            // Mark the tile as selected
            tile.addStyleClass("selectedTile");
        },

        onSelectRepairCode: function (oEvent) {
            // Get source button and its parent row
            const button = oEvent.getSource();
            const row = button.getParent();
            const rowIndex = row.getParent().indexOfItem(row);

            // Store selected row index for later use
            localStorage.ncTableSelectedRowIndex = rowIndex;

            // Get the NC code from the row
            const ncCode = row.getCells()[0].getText();

            // Open repair codes dialog
            this._openRepairCodesDialog(ncCode);
        },

        _openRepairCodesDialog: function (ncCode) {
            // Create and open repair codes dialog
            if (!this._oRepairDialog) {
                this._oRepairDialog = sap.ui.xmlfragment("production.fragments.RepairCodesDialog", this);
                this.getView().addDependent(this._oRepairDialog);
            }

            // Load repair codes for this NC code
            this._loadRepairCodes(ncCode);

            this._oRepairDialog.open();
        },

        _loadRepairCodes: function (ncCode) {
            // In real implementation, this would fetch repair codes from backend
            // For this demo, we'll use dummy data
            let repairCodes = [];
            var params = {
                site: "6423",
                ncCode: ncCode
            };
            var endPoint = "/ncRepairController/getRepairCodesByFailureCode";
            var buildUrl = Utils.buildUrl(endPoint, params);
            var callRequest = Utils.xhttpGet(buildUrl, JSON.stringify(params));
            try {
                repairCodes = JSON.parse(callRequest.response).filter(x => x.locale == localStorage.selectedLanguage);
            } catch (error) {
                console.error("Error parsing NC codes:", error);
                repairCodes = [];
            }

            // Create tiles for each repair code
            const tileContainer = sap.ui.getCore().byId("repairTileContainer");
            tileContainer.removeAllItems();

            repairCodes.forEach(code => {
                const tile = new sap.m.GenericTile({
                    header: code.description,
                    subheader: code.repairCode,
                    press: this.onRepairTilePress.bind(this)
                }).addStyleClass("sapUiSmallMargin");

                tileContainer.addItem(tile);
            });
        },

        onRepairTilePress: function (oEvent) {
            const tile = oEvent.getSource();
            const repairCode = tile.getProperty("subheader");
            const rowIndex = parseInt(localStorage.ncTableSelectedRowIndex);
            const table = sap.ui.getCore().byId("idSelectedNCsTable");
            const row = table.getItems()[rowIndex];
            if (!row) return;
            const ncCodeLabel = row.getCells()[0];
            const button = row.getCells()[2];
            const selectedNCs = this.getView().getModel("selectedNCsModel").getData().items;
            const selectedNC = selectedNCs[rowIndex];

            if (selectedNC) {
                selectedNC.repairWillLog = true;
                selectedNC.repairCode = repairCode;
                button.setText(repairCode);
            }
            this._oRepairDialog.close();
        },

        onMarkAsNotRepaired: function () {
            const rowIndex = parseInt(localStorage.ncTableSelectedRowIndex);
            const table = sap.ui.getCore().byId("idSelectedNCsTable");
            const row = table.getItems()[rowIndex];
            if (!row) return;
            const ncCodeLabel = row.getCells()[0];
            const button = row.getCells()[2];
            const selectedNCs = this.getView().getModel("selectedNCsModel").getData().items;
            const selectedNC = selectedNCs[rowIndex];
            if (selectedNC) {
                selectedNC.repairWillLog = false;
                selectedNC.repairCode = "";
                button.setText(this.getView().getModel("i18n").getResourceBundle().getText("selectRepairCode.label"));
            }
            this._oRepairDialog.close();
        },

        onCloseRepairDialog: function () {
            this._oRepairDialog.close();
        },

        onDeleteNCCode: function (oEvent) {
            const button = oEvent.getSource();
            const row = button.getParent();
            const selectedNCCode = row.getCells()[0].getText();
            const selectedRowId = oEvent.getSource().getBindingContext("selectedNCsModel").sPath.split("/")[2];
            const selectedNCsModel = this.getView().getModel("selectedNCsModel");
            const selectedNCs = selectedNCsModel.getProperty("/items")[selectedRowId];
            selectedNCsModel.setProperty("/items", selectedNCsModel.getProperty("/items").filter(nc => nc.rowId !== selectedNCs.rowId));
            selectedNCsModel.refresh();
            const flexBox = sap.ui.getCore().byId("ncTypesContainer");
            const tiles = flexBox.getItems();

            for (let i = 0; i < tiles.length; i++) {
                if (tiles[i].getProperty("subheader") === selectedNCCode) {
                    tiles[i].removeStyleClass("sapMGTSelected");
                    break;
                }
            }
        },

        onSendNCCodes: function () {
            const selectedNCsModel = this.getView().getModel("selectedNCsModel");
            const selectedNCs = selectedNCsModel.getProperty("/items");
            var resource = localStorage.selectedResource.split("-")[0].split(",")[1];
            var request = {
                site: "6423",
                resource: resource,
                ncCodes: selectedNCs
            };
            var inputJSONModel = new JSONModel();
            inputJSONModel.setData(request);
            var newElemJSON = inputJSONModel.getJSON();
            var xhttpLogNcsForSfc = Utils.xhttpPost(
                "/bekorest/restapi/ncRepairController/logNcRepair?site=" + this.site + "&workCenter=" + this.appWorkCenter.getSelectedKey() + "&resource=" + resource,
                newElemJSON);
            if (JSON.parse(xhttpLogNcsForSfc.response).success) {
                this.changeInfoText(JSON.parse(xhttpLogNcsForSfc.response).messageCode, "Accept");
            } else {
                this.changeInfoText(JSON.parse(xhttpLogNcsForSfc.response).messageCode, "Reject");
            }
            const ncsToLog = selectedNCs.filter(nc => nc.ncWillLog && !nc.repaired);
            const repairsToLog = selectedNCs.filter(nc => nc.repairWillLog);
            MessageToast.show(this.getView().getModel("i18n").getResourceBundle().getText("ncAndRepairSaved.label") + `${ncsToLog.length} NC - ${repairsToLog.length}` + this.getView().getModel("i18n").getResourceBundle().getText("repair.label"));
            this.onCloseNCDialog();
        },

        onCloseNCDialog: function () {
            if (this._oNCDialog) {
                this._oNCDialog.close();
            }
        },
        //QualityChain Actions
        // NC Login Dialog methods
        openNCLoginDialog: function () {
            this.getOwnerComponent().byId("panelView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this.getOwnerComponent().byId("traceabilityView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this.getOwnerComponent().byId("repairView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this.getOwnerComponent().byId("qualityChainView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            this.getOwnerComponent().byId("packageLabelView")?.getDependents().filter(x => x.sId = "idLoginNCDialog")[0]?.destroy();
            // Create dialog lazily
            // Create dialog via fragment factory
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
        // Explicitly set active input to username
        selectUsernameInput: function () {
            this._activeNCInput = sap.ui.getCore().byId("idNCDialogUsername");
            this._activeNCInput.focus();

            // Update active input indicator
            var indicator = sap.ui.getCore().byId("activeInputIndicator");
            if (indicator) {
                indicator.setText("Aktif Alan: Kullanıcı Adı");
            }
        },

        // Explicitly set active input to password
        selectPasswordInput: function () {
            this._activeNCInput = sap.ui.getCore().byId("idNCDialogPassword");
            this._activeNCInput.focus();

            // Update active input indicator
            var indicator = sap.ui.getCore().byId("activeInputIndicator");
            if (indicator) {
                indicator.setText("Aktif Alan: Şifre");
            }
        },

        // Add character to the active input field
        addCharToNCDialog: function (oEvent) {
            // Handle either button press event or direct character input
            var character = "";
            if (typeof oEvent === "string") {
                character = oEvent;
            } else {
                character = oEvent.getSource().getText();
            }

            if (!this._activeNCInput) {
                this._activeNCInput = sap.ui.getCore().byId("idNCDialogUsername");
            }

            if (this._activeNCInput) {
                // Get current text
                var currentText = this._activeNCInput.getValue();

                switch (character) {
                    case "delete":
                        // Handle delete key
                        if (currentText && currentText.length > 0) {
                            this._activeNCInput.setValue(currentText.substring(0, currentText.length - 1));
                        }
                        break;

                    case "space":
                        // Handle space key
                        this._activeNCInput.setValue(currentText + " ");
                        break;

                    case "shift":
                        // Handle shift key
                        this.toggleShiftMode();
                        return;

                    case "shiftLock":
                        // Handle shift lock (caps lock) key
                        this.toggleShiftLock();
                        return;

                    case "tab":
                        // Handle tab key to switch between inputs
                        if (this._activeNCInput.getId() === "idNCDialogUsername") {
                            this._activeNCInput = sap.ui.getCore().byId("idNCDialogPassword");
                            this._activeNCInput.focus();

                            // Update active input indicator
                            var activeInputIndicator = sap.ui.getCore().byId("activeInputIndicator");
                            if (activeInputIndicator) {
                                activeInputIndicator.setText("Aktif Alan: Şifre");
                            }
                        } else {
                            this._activeNCInput = sap.ui.getCore().byId("idNCDialogUsername");
                            this._activeNCInput.focus();

                            // Update active input indicator
                            var activeInputIndicator = sap.ui.getCore().byId("activeInputIndicator");
                            if (activeInputIndicator) {
                                activeInputIndicator.setText("Aktif Alan: Kullanıcı Adı");
                            }
                        }
                        break;

                    case "enter":
                        // Handle enter key
                        this.onPressNCDialogLogin();
                        break;

                    default:
                        // Handle regular keys (letters, numbers, special chars)
                        // Apply shift for letter keys if shift is enabled
                        var inputChar = character;
                        if (/^[a-zA-Z]$/.test(character)) {
                            // If shift or shift lock is enabled, convert to uppercase
                            if (this._shiftEnabled || this._shiftLockEnabled) {
                                inputChar = character.toUpperCase();
                            } else {
                                inputChar = character.toLowerCase();
                            }

                            // Turn off shift after one character (only if shift lock is not enabled)
                            if (this._shiftEnabled && !this._shiftLockEnabled) {
                                this._shiftEnabled = false;

                                // Update keyboard state
                                this.updateKeyboardKeys();
                            }
                        }

                        // Add the character to the input
                        this._activeNCInput.setValue(currentText + inputChar);
                        break;
                }
            }
        },

        // Add space to the active input field
        addSpaceToNCDialog: function () {
            var sCurrentValue = this._activeNCInput.getValue();
            this._activeNCInput.setValue(sCurrentValue + " ");
        },

        // Remove last character from the active input field
        removeCharFromNCDialog: function () {
            var sCurrentValue = this._activeNCInput.getValue();
            if (sCurrentValue.length > 0) {
                this._activeNCInput.setValue(sCurrentValue.substring(0, sCurrentValue.length - 1));
            }
        },



        // Handle cancel button press
        onPressNCDialogCancel: function () {
            // Close dialog and switch back to the previous tab
            this._oNCLoginDialog.close();
            this.getView().byId("idIconTabBar")?.setSelectedKey("materialList");
        },
        // Toggle shift mode for uppercase/lowercase
        toggleShiftMode: function () {
            this._shiftEnabled = !this._shiftEnabled;
            this.updateKeyboardKeys();

            // If shift lock is enabled, disable it when shift is toggled off
            if (this._shiftLockEnabled && !this._shiftEnabled) {
                this._shiftLockEnabled = false;
            }
        },
        // Toggle shift lock mode (caps lock)
        toggleShiftLock: function () {
            this._shiftLockEnabled = !this._shiftLockEnabled;

            // When enabling shift lock, disable shift
            if (this._shiftLockEnabled) {
                this._shiftEnabled = false;
            }

            this.updateKeyboardKeys();
        },
        // Helper function to update keyboard button text based on shift/shift lock state
        _updateKeyboardButtonsCase: function () {
            // Determine if uppercase should be used
            var useUpperCase = this._shiftEnabled || this._shiftLockEnabled;

            // Update all letter buttons
            var letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];

            for (var i = 0; i < letters.length; i++) {
                var letter = letters[i];
                var button = sap.ui.getCore().byId("key" + letter);
                if (button) {
                    button.setText(useUpperCase ? letter : letter.toLowerCase());
                }
            }
        },

        createNCKeyboard: function () {
            var oKeyboard = new sap.m.VBox({
                id: "keyboardContainer",
                width: "100%",
                items: []
            });

            // Row 1: Numbers
            var oRow1 = new sap.m.HBox({
                width: "100%",
                renderType: "Bare",
                justifyContent: "SpaceBetween"
            });

            for (var i = 1; i <= 9; i++) {
                oRow1.addItem(
                    new sap.m.Button({
                        text: i.toString(),
                        width: "10%",
                        press: function (oEvent) {
                            this.addCharToNCDialog(oEvent.getSource().getText());
                        }.bind(this)
                    })
                );
            }

            oRow1.addItem(
                new sap.m.Button({
                    text: "0",
                    width: "10%",
                    press: function (oEvent) {
                        this.addCharToNCDialog(oEvent.getSource().getText());
                    }.bind(this)
                })
            );

            // Row 2: QWERTYUIOP
            var oRow2 = new sap.m.HBox({
                width: "100%",
                renderType: "Bare",
                justifyContent: "SpaceBetween"
            });

            var row2Keys = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"];
            for (var i = 0; i < row2Keys.length; i++) {
                var key = row2Keys[i];
                oRow2.addItem(
                    new sap.m.Button({
                        id: "key_" + key,
                        text: key,
                        width: "10%",
                        press: function (oEvent) {
                            this.addCharToNCDialog(oEvent.getSource().getText().toLowerCase());
                        }.bind(this)
                    })
                );
            }

            // Row 3: ASDFGHJKL
            var oRow3 = new sap.m.HBox({
                width: "100%",
                renderType: "Bare",
                justifyContent: "SpaceBetween"
            });

            // Add Caps Lock button to the left of 'a'
            oRow3.addItem(
                new sap.m.Button({
                    id: "shiftLockButton",
                    text: "Caps",
                    width: "10%",
                    press: function () {
                        this.addCharToNCDialog("shiftLock");
                    }.bind(this)
                })
            );

            var row3Keys = ["a", "s", "d", "f", "g", "h", "j", "k", "l"];
            for (var i = 0; i < row3Keys.length; i++) {
                var key = row3Keys[i];
                oRow3.addItem(
                    new sap.m.Button({
                        id: "key_" + key,
                        text: key,
                        width: "10%",
                        press: function (oEvent) {
                            this.addCharToNCDialog(oEvent.getSource().getText().toLowerCase());
                        }.bind(this)
                    })
                );
            }

            // Row 4: ZXCVBNM + Special
            var oRow4 = new sap.m.HBox({
                width: "100%",
                renderType: "Bare",
                justifyContent: "SpaceBetween"
            });

            // Add Shift button to the left of 'z'
            oRow4.addItem(
                new sap.m.Button({
                    id: "shiftButton",
                    text: "Shift",
                    width: "10%",
                    press: function () {
                        this.addCharToNCDialog("shift");
                    }.bind(this)
                })
            );

            var row4Keys = ["z", "x", "c", "v", "b", "n", "m"];
            for (var i = 0; i < row4Keys.length; i++) {
                var key = row4Keys[i];
                oRow4.addItem(
                    new sap.m.Button({
                        id: "key_" + key,
                        text: key,
                        width: "10%",
                        press: function (oEvent) {
                            this.addCharToNCDialog(oEvent.getSource().getText().toLowerCase());
                        }.bind(this)
                    })
                );
            }

            // Add Delete button to the right of 'm'
            oRow4.addItem(
                new sap.m.Button({
                    text: "Sil",
                    width: "10%",
                    press: function () {
                        this.addCharToNCDialog("delete");
                    }.bind(this)
                })
            );

            // Add Tab button
            oRow4.addItem(
                new sap.m.Button({
                    text: "Tab",
                    width: "10%",
                    press: function () {
                        this.addCharToNCDialog("tab");
                    }.bind(this)
                })
            );

            // Row 5: Space and Enter
            var oRow5 = new sap.m.HBox({
                width: "100%",
                renderType: "Bare",
                justifyContent: "SpaceBetween"
            });

            oRow5.addItem(
                new sap.m.Button({
                    text: "Space",
                    width: "70%",
                    press: function () {
                        this.addCharToNCDialog("space");
                    }.bind(this)
                })
            );

            oRow5.addItem(
                new sap.m.Button({
                    text: "Enter",
                    width: "30%",
                    press: function () {
                        this.addCharToNCDialog("enter");
                    }.bind(this)
                })
            );

            // Row for indicators
            var oIndicatorRow = new sap.m.HBox({
                width: "100%",
                renderType: "Bare",
                justifyContent: "SpaceBetween"
            });

            // Add input indicator
            oIndicatorRow.addItem(
                new sap.m.Text({
                    id: "activeInputIndicator",
                    text: "Aktif Input: Username"
                })
            );

            // Add shift state indicator
            oIndicatorRow.addItem(
                new sap.m.Text({
                    id: "shiftStateIndicator",
                    text: "Shift: Kapalı"
                })
            );

            // Add caps lock state indicator
            oIndicatorRow.addItem(
                new sap.m.Text({
                    id: "capsLockStateIndicator",
                    text: "Caps Lock: Kapalı"
                })
            );

            // Add all rows to the keyboard
            oKeyboard.addItem(oIndicatorRow);
            oKeyboard.addItem(oRow1);
            oKeyboard.addItem(oRow2);
            oKeyboard.addItem(oRow3);
            oKeyboard.addItem(oRow4);
            oKeyboard.addItem(oRow5);

            // Initialize keyboard state
            this._shiftEnabled = false;
            this._shiftLockEnabled = false;

            return oKeyboard;
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
                this.focusFirstInput();
            }
        },
        updateKeyboardKeys: function () {
            // Update all letter keys based on shift and shift lock state
            var isUpperCase = this._shiftEnabled || this._shiftLockEnabled;

            // Update shift button appearance
            var shiftButton = sap.ui.getCore().byId("shiftButton");
            if (shiftButton) {
                shiftButton.setType(this._shiftEnabled ? "Emphasized" : "Default");
            }

            // Update shift lock button appearance
            var shiftLockButton = sap.ui.getCore().byId("shiftLockButton");
            if (shiftLockButton) {
                shiftLockButton.setType(this._shiftLockEnabled ? "Emphasized" : "Default");
            }

            // Update all letter keys
            var letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];

            for (var i = 0; i < letters.length; i++) {
                var letter = letters[i];
                var button = sap.ui.getCore().byId("key" + letter);
                if (button) {
                    button.setText(isUpperCase ? letter : letter.toLowerCase());
                }
            }

            // Update shift state indicator
            var shiftIndicator = sap.ui.getCore().byId("shiftStateIndicator");
            if (shiftIndicator) {
                if (this._shiftLockEnabled) {
                    shiftIndicator.setText("Caps Lock: Açık");
                } else {
                    shiftIndicator.setText("Shift: " + (this._shiftEnabled ? "Açık" : "Kapalı"));
                }
            }
        },
    });

});