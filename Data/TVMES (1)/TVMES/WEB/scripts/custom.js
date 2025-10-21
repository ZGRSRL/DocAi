function testFunc(p1, p2) {
	return p1 * p2;   // The function returns the product of p1 and p2
}

function groupBy(collection, property) {
	var i = 0, val, index,
		values = [], result = [];
	for (; i < collection.length; i++) {
		val = collection[i][property];
		index = values.indexOf(val);
		if (index > -1)
			result[index].push(collection[i]);
		else {
			values.push(val);
			result.push([collection[i]]);
		}
	}
	return result;
}

function GetLoginName() {
	try {
		var url = "/XMII/PropertyAccessServlet?mode=Retrieve&PropName=IllumLoginName&Content-Type=text/json";
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.onreadystatechange = function () {
			if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
				var oUserData = JSON.parse(xmlHttp.responseText);
			} else {
				return "";
			}
		}
		xmlHttp.open("POST", url, false);
		xmlHttp.send(null);
		return JSON.parse(xmlHttp.responseText).Rowsets.Rowset[0].Row[0].Value;
	}
	catch (E) {
		location.reload();
	}
}

function GetLanguage() {
	try {
		var url = "/XMII/PropertyAccessServlet?mode=Retrieve&PropName=Language&Content-Type=text/json";
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.onreadystatechange = function () {
			if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
				var oUserData = JSON.parse(xmlHttp.responseText);
			} else {
				return "";
			}
		}
		xmlHttp.open("POST", url, false);
		xmlHttp.send(null);
		return JSON.parse(xmlHttp.responseText).Rowsets.Rowset[0].Row[0].Value;
	}
	catch (E) {
		location.reload();
	}
}

function GetSite() {
	try {
		var url = "/XMII/PropertyAccessServlet?mode=Retrieve&PropName=DEFAULT%20SITE&Content-Type=text/json";
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.onreadystatechange = function () {
			if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
				var oUserData = JSON.parse(xmlHttp.responseText);
			} else {
				return "";
			}
		}
		xmlHttp.open("POST", url, false);
		xmlHttp.send(null);
		return JSON.parse(xmlHttp.responseText).Rowsets.Rowset[0].Row[0].Value;
	}
	catch (E) {
		location.reload();
	}
}

function TransactionRunner(p_tcode, params) {
	var m_url = "";
	var m_parameters = "";
	var m_header = { "content-type": "text/json" };
	var m_tcode = p_tcode;
	//var m_xmlHttp = new XMLHttpRequest();
	var m_jsonDOC;
	var m_errormessage = "";
	var m_message = "";
	var m_error = false;
	var m_jsondata;
	var that = this;

	if (params) {
		var keys = Object.keys(params);
		keys.forEach(function (oKey) {
			if (m_parameters.length > 0) m_parameters += "&";
			m_parameters += oKey + "=" + params[oKey];
			m_header[oKey] = params[oKey];
		});
	}

	this.AddParameter = function (p_name, p_value) {
		if (m_parameters.length > 0) m_parameters += "&";
		// m_parameters += p_name + "=" + p_value;
		m_parameters += p_name + "=" + p_value; // this.transformParameter(p_value); // value alanı özel karakter içerebileceği için encode edildi, tek tırnak işareti (') çiftelenerek sql'e uyumlu hale getirildi ('')
		m_header[p_name] = p_value;
	}

	this.Execute = function () {
		var lv_url = this.GetURL();
		var lv_params = this.GetParameters();
		if (!SendHttpRequest(lv_url, lv_params))
			return false;
		if (!GetJSONObject())
			return false;
		return true;
	}

	this.GetURL = function () {
		var urlArry = m_tcode.split("/");
		m_url = "/XMII/Illuminator?QueryTemplate=" + m_tcode + "&Content-Type=text/json";
		return m_url;
	}

	this.GetParameters = function () {
		return m_parameters;
	}

	this.transformParameter = function (oParam) {
		var param = oParam.toString().replaceAll("'", "''");
		param = param.replaceAll("\r\n", "");
		param = param.replaceAll("\n", "");
		param = encodeURIComponent(param);
		return param;
	}


	this.ExecuteAsync = function (p_controller, p_callback) {
		var lv_url = this.GetURL();
		var lv_params = this.GetParameters();
		SendHttpRequestAsync(lv_url, lv_params, p_controller, p_callback);
		return true;
	}
	var SendHttpRequestAsync = function (p_url, p_params, p_controller, p_callback) {
		ClearErrorMessage();

		try {
			var xhr = $.ajax({
				type: "POST",
				url: p_url,
				data: p_params,
				async: true,
				success: function () {
					if (xhr.readyState === 4) {
						if (xhr.status === 200) {
							m_jsonDOC = xhr.responseText;
							var success = GetJSONObject();
							if (p_controller) {
								p_callback(p_controller, m_jsondata, that);
							}
							return true;
						} else {
							SetErrorMessage("01-Ajax çağrısı esnasında hata oluştu. Hata: " + xhr.statusText);
						}
					}
				}
			});

		} catch (err) {
			console.log(err);
			SetErrorMessage("02-Ajax çağrısı esnasında hata oluştu. Hata:" + err.message);
			return false;
		}
	}

	this.ExecuteQueryAsync = function (p_controller, p_callback) {
		//	var lv_params = this.GetParameters();
		m_header.QueryTemplate = m_tcode;
		$.ajax({
			url: "/XMII/Illuminator",
			type: 'POST',
			dataType: 'json',
			data: m_header,
			cache: false,
			async: true,
			success: function (data, textStatus, jqXHR) {
				if (!data.Rowsets.Rowset) {
					if (data.Rowsets.FatalError) {
						sap.m.MessageBox.show(data.Rowsets.FatalError, { title: "System" });
						//MessageBox.error(data.Rowsets.FatalError, {title:"System"});
					} else {
						//	MessageToast.show("Kritere uygun data bulunamadı."); 
						p_callback(p_controller, {}, this);
					}
					return false;
				}
				p_callback(p_controller, data, this);
				return true;
			}
		});
	}

	var SendHttpRequest = function (p_url, p_params) {
		ClearErrorMessage();

		try {
			var jsonHttp = $.ajax({
				type: "POST",
				url: p_url,
				data: p_params,
				async: false,
				dataType: "json"
			});

			if (jsonHttp.status == "200") {
				m_jsonDOC = jsonHttp.responseJSON;
				if(!m_jsonDOC){
					if(jsonHttp.responseText.length> 0){
						window.location.reload();
					}
				}
				return true;
			}
			else if (jsonHttp.status == "500") {
				window.location.reload();
				return false;
			}
			else {
				SetErrorMessage("01-Ajax çağrısı esnasında hata oluştu. Hata:" + jsonHttp.status + " : " + jsonHttp.statusText + " URL: " + p_url + " Data:" + p_params);
				return false;
			}

		} catch (err) {
			console.log(err);
			SetErrorMessage("02-Ajax çağrısı esnasında hata oluştu. Hata:" + err.message);
			return false;
		}
	}

	var GetJSONObject = function () {
		ClearErrorMessage();

		var lo_jsonDOM = m_jsonDOC; //.documentElement;

		if (lo_jsonDOM.Rowsets.FatalError != null) {
			var opElement = lo_jsonDOM.Rowsets.FatalError;
			SetErrorMessage(opElement);
			return false;
		}

		if (lo_jsonDOM.Rowsets.Rowset) {
			try {
				var jsData = lo_jsonDOM;
				if (jsData.Rowsets) {
					var columnData = jsData.Rowsets.Rowset[0].Columns.Column;
					var rowData = jsData.Rowsets.Rowset[0].Row;
					m_jsondata = [{ "Column": columnData, "Row": rowData }];
				}
				return true;
			} catch (err) {
				console.log(err);
				SetErrorMessage(err.message);
				return false;
			}
		}

		if (lo_jsonDOM.Rowsets.Messages) {
			var opElement = lo_jsonDOM.Rowsets.Messages[0].Message;
			if (opElement == "No Data Returned") {
				lo_jsonDOM.Rowsets.Rowset = [];
				lo_jsonDOM.Rowsets.Rowset[0] = { Row: [] }
				m_jsondata = [{ "Row": lo_jsonDOM.Rowsets.Rowset[0].Row }];
				// SetErrorMessage(p_tcode + " -- " + m_parameters + " --Transaction sonuç dönmedi.");
				// return false;
				return true;
			}
			SetMessage(opElement);
			return true;
		}

		SetErrorMessage(p_tcode + " -- " + m_parameters + " --Transaction sonuç dönmedi.");
		return false;
	}

	this.GetJSONData = function () {
		return m_jsondata;
	}

	this.IsError = function () {
		return m_error;
	}

	this.GetErrorMessage = function () {
		return m_errormessage;
	}

	var SetErrorMessage = function (p_message) {
		m_error = true;
		m_errormessage = p_message;
	}

	var ClearErrorMessage = function () {
		m_error = false;
		m_errormessage = "";
	}

	this.GetMessage = function () {
		return m_message;
	}

	var SetMessage = function (p_message) {
		m_message = p_message;
	}

}


/*function datenow() {

	var date = new Date();
	var yyyy = date.getFullYear();
	var gg = date.getDate();
	var mm = (date.getMonth() + 1);

	if (gg < 10)
		gg = "0" + gg;

	if (mm < 10)
		mm = "0" + mm;

	var cur_day = yyyy + "-" + mm + "-" + gg;

	var hours = date.getHours()
	var minutes = date.getMinutes()
	var seconds = date.getSeconds();

	if (hours < 10)
		hours = "0" + hours;

	if (minutes < 10)
		minutes = "0" + minutes;

	if (seconds < 10)
		seconds = "0" + seconds;

	return cur_day + " " + hours + ":" + minutes + ":" + seconds;

}*/

function dateTimeNow() {

	var date = new Date();
	var yyyy = date.getFullYear();
	var gg = date.getDate();
	var mm = (date.getMonth() + 1);

	if (gg < 10)
		gg = "0" + gg;

	switch (mm) {
		case 1: mm = "Ocak";
			break;
		case 2: mm = "Şubat";
			break;
		case 3: mm = "Mart";
			break;
		case 4: mm = "Nisan";
			break;
		case 5: mm = "Mayıs";
			break;
		case 6: mm = "Haziran";
			break;
		case 7: mm = "Temmuz";
			break;
		case 8: mm = "Ağustos";
			break;
		case 9: mm = "Eylül";
			break;
		case 10: mm = "Ekim";
			break;
		case 11: mm = "Kasım";
			break;
		case 12: mm = "Aralık";
			break;
	};

	var cur_day = gg + " " + mm + " " + yyyy;

	var hours = date.getHours()
	var minutes = date.getMinutes()
	var seconds = date.getSeconds();

	if (hours < 10)
		hours = "0" + hours;

	if (minutes < 10)
		minutes = "0" + minutes;

	if (seconds < 10)
		seconds = "0" + seconds;

	return cur_day + " " + hours + ":" + minutes + ":" + seconds;

}

function dateNow() {
	var date = new Date();
	var yyyy = date.getFullYear();
	var gg = date.getDate();
	var mm = (date.getMonth() + 1);

	if (gg < 10)
		gg = "0" + gg;

	switch (mm) {
		case 1: mm = "Ocak";
			break;
		case 2: mm = "Şubat";
			break;
		case 3: mm = "Mart";
			break;
		case 4: mm = "Nisan";
			break;
		case 5: mm = "Mayıs";
			break;
		case 6: mm = "Haziran";
			break;
		case 7: mm = "Temmuz";
			break;
		case 8: mm = "Ağustos";
			break;
		case 9: mm = "Eylül";
			break;
		case 10: mm = "Ekim";
			break;
		case 11: mm = "Kasım";
			break;
		case 12: mm = "Aralık";
			break;
	};

	return gg + " " + mm + " " + yyyy;
}

function timeNow() {
	var date = new Date();
	var hours = date.getHours()
	var minutes = date.getMinutes()
	var seconds = date.getSeconds();

	if (hours < 10)
		hours = "0" + hours;

	if (minutes < 10)
		minutes = "0" + minutes;

	if (seconds < 10)
		seconds = "0" + seconds;

	return hours + ":" + minutes + ":" + seconds;

}

function dateTimePeriodStart(howManyHoursAgo) {
	if(howManyHoursAgo == "" || !howManyHoursAgo) howManyHoursAgo = 0
	var date = new Date();
	date.setUTCHours(date.getUTCHours() - howManyHoursAgo);
	var yyyy = date.getFullYear();
	var gg = date.getDate();
	var mm = (date.getMonth() + 1);
	var hours = date.getHours()
	var minutes = date.getMinutes()
	var seconds = date.getSeconds();

	if (mm < 10)
		mm = "0" + mm;

	if (gg < 10)
		gg = "0" + gg;

	if (hours < 10)
		hours = "0" + hours;

	if (minutes < 10)
		minutes = "0" + minutes;

	if (seconds < 10)
		seconds = "0" + seconds;

	//return yyyy + "-" + mm + "-" + gg + " " + hours + ":" + minutes + ":" + seconds;
	return mm + "/" + gg + "/" + yyyy + " " + hours + ":" + minutes + ":" + seconds;

}

function getFormattedPastTime(secondsAgo) {
  var now = new Date();
  var past = new Date(now.getTime() - secondsAgo * 1000);

  var day = past.getDate();
  var month = past.getMonth() + 1; // JavaScript'te aylar 0'dan başlar (0 = Ocak)
  var year = past.getFullYear();

  var hours = past.getHours();
  var minutes = past.getMinutes();
  var seconds = past.getSeconds();

  // Sayılar tek basamaklıysa başlarına 0 ekleyerek formatlıyoruz
  day = day < 10 ? '0' + day : day;
  month = month < 10 ? '0' + month : month;
  hours = hours < 10 ? '0' + hours : hours;
  minutes = minutes < 10 ? '0' + minutes : minutes;
  seconds = seconds < 10 ? '0' + seconds : seconds;

  var formattedTime = `${month}/${day}/${year} ${hours}:${minutes}:${seconds}`;
  return formattedTime;
}


function GetGlobalVariable() {
	try {
		var url = "/XMII/Catalog?Mode=Load&Class=Globals&TemporaryFile=false&Content-Type=text/json";
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.onreadystatechange = function () {
			if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
				var oUserData = JSON.parse(xmlHttp.responseText);
			} else {
				return "";
			}
		}
		xmlHttp.open("POST", url, false);
		xmlHttp.send(null);
		return JSON.parse(xmlHttp.responseText).Rowsets.Rowset[0].Row[0].Value;
	}
	catch (E) {
		location.reload();
	}
}

function GetLoginRoles() {
	try {
		var url = "/XMII/PropertyAccessServlet?mode=Retrieve&PropName=IllumLoginRoles&Content-Type=text/json";
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.onreadystatechange = function () {
			if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
				var oUserData = JSON.parse(xmlHttp.responseText);
			} else {
				return "";
			}
		}
		xmlHttp.open("POST", url, false);
		xmlHttp.send(null);
		return JSON.parse(xmlHttp.responseText).Rowsets.Rowset[0].Row[0].Value;
	}
	catch (E) {
		console.log(E)
	}
}


var GetAlertList = function (p_controller, p_callback) {
	var p_url = "/XMII/Illuminator?Service=Alert&mode=GetAlerts&content-type=text/json"
	var p_params = "containerPropertyName=Loc&Status=New";
	var xhr = $.ajax({
		type: "POST",
		url: p_url,
		data: p_params,
		async: true,
		success: function () {
			if (xhr.readyState === 4) {
				if (xhr.status === 200) {
					m_jsonDOC = xhr.responseText;
					if (p_controller) {
						p_callback(p_controller, m_jsondata, that);
					}
					return true;
				} else {
					SetErrorMessage("01-Ajax çağrısı esnasında hata oluştu. Hata: " + xhr.statusText);
				}
			}
		}
	});

}
