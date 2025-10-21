sap.ui.define([
    "sap/ui/core/format/DateFormat"
], (DateFormat) => {
    "use strict";

    return {

        getText: function(messageKey, defaultText) {
            if (messageKey) {
                return this.getView().getModel("i18n").getResourceBundle().getText(messageKey);
            }
            return defaultText;
        },
        formattedDate(data) {
            var date = new Date(data);
            var dateFormat = sap.ui.core.format.DateFormat.getDateInstance({ pattern: "dd/MM/YYYY HH:mm:ss" });
            var dateFormatted = dateFormat.format(date);
            return dateFormatted;
        }, removeLeadingZeros: function (sValue) {
            if (sValue) {
                return sValue.replace(/^0+/, '');
            }
            return sValue;
        },
toString(data){
			return ""+data;
		}
    };
});