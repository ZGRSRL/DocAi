jQuery.sap.declare("production.scripts.Utils");
jQuery.sap.require("sap.ui.model.Filter");
production.scripts.Utils = function () {
  var urlPrefix = "/bekorest/restapi";

  // Helper function to check if current URL is 127.0.0.1:8080
  function isLocalHost() {
    return window.location.href.startsWith("http://127.0.0.1:8080/");
  }
  function getHostName(){
	return   window.location.origin.split("//")[1];
}
  function parseXML(xmlString) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlString, "text/xml");
    return xmlDoc;
  }
  // Helper to modify URLs for local development
  function getModifiedUrl(url) {
    if (isLocalHost() && !url.startsWith("http")) {
      return getHostName() + url;
    }
    return url;
  }

  return {
    asyncGET: function (url, fnCallback) {
      url = getModifiedUrl(url);
      $.ajax({
        url: url,
        type: "GET",
        headers: {
          "Authorization": "Basic a2VuYW50OkFyMTIzNDU2"
        },
        dataType: "json",
        success: function (response) {
          fnCallback(response);
        },
        error: function (xhr, status, error) {
	 let errorJson = {
              "success" : false,
              "messageCode": "29989.error.label",
              "errorMessage": "Unexpected error" 
          }
          fnCallback(errorJson);
          console.error("Hata:", status, error);
        }
      });
    },
    asyncPOST: function (url, fnCallback) {
      url = getModifiedUrl(url);
      $.ajax({
        url: url,
        type: "POST",
        headers: {
          "Authorization": "Basic a2VuYW50OkFyMTIzNDU2"
        },
        contentType: "application/json",
        dataType: "json",
        success: function (response) {
          fnCallback(response);
        },
        error: function (xhr, status, error) {
          let errorJson = {
              "success" : false,
              "messageCode": "29989.error.label",
              "errorMessage": "Unexpected error" 
          }
          fnCallback(errorJson);
          console.error("Hata:", status, error);
        }
      });
    },
    asyncPOSTBody: function (url, data, fnCallback) {
      url = getModifiedUrl(url);
      $.ajax({
        url: url,
        type: "POST",
        contentType: "application/json",
        dataType: "json",
        headers: {
          "Authorization": "Basic VFZfVVNFUjpBcjEyMzQ1Ng=="
        },
        data: JSON.stringify(data),
        success: function (response) {
          fnCallback(response);
        },
        error: function (xhr, status, error) {
          console.error("Hata:", status, error);
        }
      });
    },
    xhttpGet: function (uri) {
      uri = getModifiedUrl(uri);
      var xhttpGet = new XMLHttpRequest();
      xhttpGet.open("GET", uri, false);
      xhttpGet.setRequestHeader("Content-type", "application/json;charset=utf-8");
      xhttpGet.setRequestHeader("Accept", "application/json;charset=utf-8");
      xhttpGet.setRequestHeader("Cache-Control", "no-cache,max-age=0");
      xhttpGet.setRequestHeader("Authorization", "Basic VFZfVVNFUjpBcjEyMzQ1Ng==")
      xhttpGet.setRequestHeader("pragma", "no-cache");
      xhttpGet.send();
      return xhttpGet;
    },
    getFormID: function () {
      var uri = "/manufacturing-rest/web-api/xsrf/generateFormId";
      uri = getModifiedUrl(uri);
      var xhttpGet = new XMLHttpRequest();
      xhttpGet.open("GET", uri, false);
      xhttpGet.setRequestHeader("Accept", "*/*");
      xhttpGet.setRequestHeader("Authorization", "Basic VFZfVVNFUjpBcjEyMzQ1Ng==")
      xhttpGet.send();
      return JSON.parse(xhttpGet.responseText).FORM_ID;
    },
    getFormIDLogin: function (username, password) {
      var uri = "/manufacturing-rest/web-api/xsrf/generateFormId";
      var credentials = btoa(username + ":" + password);
      uri = getModifiedUrl(uri);
      var xhttpGet = new XMLHttpRequest();
      xhttpGet.open("GET", uri, false);
      xhttpGet.setRequestHeader("Accept", "*/*");
      xhttpGet.setRequestHeader("Authorization", "Basic " + credentials);
      xhttpGet.send();
      return xhttpGet;
    },
    xhttpPost: function (uri, jsonBody) {
      uri = getModifiedUrl(uri);
      var xhttpPost = new XMLHttpRequest();
      xhttpPost.open("POST", uri, false);
      xhttpPost.setRequestHeader("Content-type", "application/json;charset=utf-8");
      xhttpPost.setRequestHeader("Authorization", "Basic VFZfVVNFUjpBcjEyMzQ1Ng==")
      xhttpPost.setRequestHeader("Accept", "application/json;charset=utf-8");
      if (jsonBody) xhttpPost.send(jsonBody);
      else xhttpPost.send();
      return xhttpPost;
    },
    buildUrl: function (url, parameters) {
      var qs = "";
      for (var key in parameters) {
        var value = parameters[key];
        if (value === undefined || value === null) continue;
        qs += encodeURIComponent(key) + "=" + encodeURIComponent(value) + "&";
      }
      if (qs.length > 0) {
        qs = qs.substring(0, qs.length - 1);
        url = url + "?" + qs;
      }

      var fullUrl = urlPrefix + url;

      if (isLocalHost()) {
        return getHostName() + fullUrl;
      }

      return fullUrl;
    },
    toUpperCase: function (value) {
      if (value.trim() !== "") {
        value = value.trim().toUpperCase();
      } else {
        value = "";
      }
      return value;
    },
    handleSearch: function (oValue, propertiesArray, oBinding) {
      var aFilters = [], filter, oFilterWithAllProperties;
      if (oValue && oValue.length > 0) {
        $.each(propertiesArray, function (oIndex, oObj) {
          filter = new sap.ui.model.Filter(oObj, sap.ui.model.FilterOperator.Contains, oValue);
          aFilters.push(filter);
        });
        oFilterWithAllProperties = new sap.ui.model.Filter({ filters: aFilters, and: false });
      }
      oBinding.filter(oFilterWithAllProperties);
    },

    showErrorMessage: function (messageText) {
      sap.m.MessageBox.error(messageText, {
        title: "Hata", // default
        onClose: null, // default
        styleClass: "", // default
        actions: sap.m.MessageBox.Action.CLOSE, // default
        emphasizedAction: null, // default
        initialFocus: null, // default
        textDirection: sap.ui.core.TextDirection.Inherit // default
      });
    },
    whoAmI: function () {
      var uri = "/XMII/Illuminator?service=admin&mode=CurrentProfile&content-type=text/xml";
      if (isLocalHost()) {
        uri = getHostName() + uri;
      }
      var xhttpGet = new XMLHttpRequest();
      xhttpGet.open("GET", uri, false);
      xhttpGet.send();
      return xhttpGet;
    },
    extractIllumLoginName: function (xmlString) {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlString, "text/xml");
      // Get the Profile element and read the IllumLoginName attribute
      const profileElement = xmlDoc.getElementsByTagName("Profile")[0];
      if (profileElement) {
        return profileElement.getAttribute("IllumLoginName");
      }
      return null;
    }
  };
}();