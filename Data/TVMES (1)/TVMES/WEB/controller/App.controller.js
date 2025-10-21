sap.ui.define([
	"production/controller/BaseController",
	"../scripts/customStyle",
	"../scripts/custom",
	"production/scripts/Utils",
	"sap/m/MessageBox",
	"sap/m/Dialog",
	"sap/m/Label",
	"sap/m/Input",
	"sap/m/MessageToast",
	"sap/ui/model/json/JSONModel",
	"production/scripts/WebSocketManager",
	"sap/ui/model/resource/ResourceModel"
], function (BaseController, customStyle, custom, Utils, MessageBox, Dialog, Label, Input, MessageToast, JSONModel, WebSocket, ResourceModel) {
	"use strict";
	var getTimeIntVal;
	return BaseController.extend("production.controller.App", {

		onInit: function () {
			this.resourceType = "MONTAJ";
			this.getTime();
			this.loadWorkCenters();

			// Kayıtlı dil tercihini kontrol et
			var savedLanguage = localStorage.getItem("selectedLanguage") || "tr";
			
			// Dil combobox'ını güncelle
			var languageCombo = this.byId("idLanguageCombo");
			languageCombo.setSelectedKey(savedLanguage);
			
			// i18n modelini seçilen dile göre ayarla
			this.setLanguage(savedLanguage);
		},

		setLanguage: function(language) {
			var i18nModel = new ResourceModel({
				bundleName: "production.i18n.i18n_" + language
			});
			
			// i18n modelini component'e set et
			this.getOwnerComponent().setModel(i18nModel, "i18n");
		},

		onChangeLanguage: function(oEvent) {
			var selectedKey = oEvent.getParameter("selectedItem").getKey();
			
			// Dil tercihini localStorage'a kaydet
			localStorage.setItem("selectedLanguage", selectedKey);
			
			// Dili değiştir
			this.setLanguage(selectedKey);
			
			// View'ı yenile
			this.getView().invalidate();
			
			// Dil değişikliği mesajını göster
			var messages = {
				"tr": "Dil TR olarak değiştirildi",
				"en": "Language changed to EN",
				"bn": "ভাষা BD তে পরিবর্তন করা হয়েছে"
			};
			MessageToast.show(messages[selectedKey]);
		},
		getTime: function () {
			this.clearGetTime();
			this.byId("idClock").setText(timeNow());
			getTimeIntVal = setInterval(this.getTime.bind(this), 1000);
		},
		clearGetTime: function () {
			if (!getTimeIntVal) return;
			clearInterval(getTimeIntVal);
			getTimeIntVal = null;
		},
		onPressHome: function () {
			this.getRouter().navTo("appHome");
		},
		onPressRefresh: function(){
			this.getActiveSFCInformation();
		},

	});

});

