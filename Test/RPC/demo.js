var ws = new WebSocket("ws://127.0.0.1:9999");
console.log()
ws.onopen = function () {
    console.log("open");
    ws.send("hello");
};
ws.onmessage = function (evt) {
    console.log(evt.data)
};
ws.onclose = function (evt) {
    console.log("WebSocketClosed!");
};
ws.onerror = function (evt) {
    console.log("WebSocketError!");
};


!function () {
    if (!window._makeRequest) {
        window._makeRequest = 'makeRequest';
        var ws = new WebSocket("ws://127.0.0.1:16666");
        ws.open = function (param) {
        };
        ws.onmessage = function (param) {
            var mdata = param.data;
            var u = mdata.split('|')[0]
            var p = mdata.split('|')[1]
            var result = window._makeRequest(u, p, 7, false);
            ws.send(JSON.stringify(result))
        }
    }
}();




function Hlclient(wsURL) {
    this.wsURL = wsURL;
    this.handlers = {};
    this.socket = {};
    if (!wsURL) {
        throw new Error('wsURL can not be empty!!')
    }
    this.connect()
    this.handlers["_execjs"] = function (resolve, param) {
        var res = eval(param)
        if (!res) {
            resolve("没有返回值")
        } else {
            resolve(res)
        }

    }
}
Hlclient.prototype.connect = function () {
    console.log('begin of connect to wsURL: ' + this.wsURL);
    var _this = this;
    try {
        this.socket["ySocket"] = new WebSocket(this.wsURL);
        this.socket["ySocket"].onmessage = function (e) {
            try {
                let blob = e.data
                blob.text().then(data => {
                    _this.handlerRequest(data);
                })
            } catch {
                console.log("not blob")
                _this.handlerRequest(blob)
            }

        }
    } catch (e) {
        console.log("connection failed,reconnect after 10s");
        setTimeout(function () {
            _this.connect()
        }, 10000)
    }
    this.socket["ySocket"].onclose = function () {
        console.log("connection failed,reconnect after 10s");
        setTimeout(function () {
            _this.connect()
        }, 10000)
    }

};
Hlclient.prototype.send = function (msg) {
    this.socket["ySocket"].send(msg)
}
Hlclient.prototype.regAction = function (func_name, func) {
    if (typeof func_name !== 'string') {
        throw new Error("an func_name must be string");
    }
    if (typeof func !== 'function') {
        throw new Error("must be function");
    }
    console.log("register func_name: " + func_name);
    this.handlers[func_name] = func;
    return true

}
//收到消息后这里处理，
Hlclient.prototype.handlerRequest = function (requestJson) {
    var _this = this;
    try {
        var result = JSON.parse(requestJson)
    } catch (error) {
        console.log("catch error", requestJson);
        result = transjson(requestJson)
    }
    //console.log(result)
    if (!result['action']) {
        this.sendResult('', 'need request param {action}');
        return
    }
    var action = result["action"]
    var theHandler = this.handlers[action];
    if (!theHandler) {
        this.sendResult(action, 'action not found');
        return
    }
    try {
        if (!result["param"]) {
            theHandler(function (response) {
                _this.sendResult(action, response);
            })
        } else {
            var param = result["param"]
            try {
                param = JSON.parse(param)
            } catch (e) {
                console.log("")
            }
            theHandler(function (response) {
                _this.sendResult(action, response);
            }, param)
        }

    } catch (e) {
        console.log("error: " + e);
        _this.sendResult(action + e);
    }
}
Hlclient.prototype.sendResult = function (action, e) {
    this.send(action + atob("aGxeX14") + e);
}
function transjson(formdata) {
    var regex = /"action":(?<actionName>.*?),/g
    var actionName = regex.exec(formdata).groups.actionName
    stringfystring = formdata.match(/{..data..:.*..\w+..:\s...*?..}/g).pop()
    stringfystring = stringfystring.replace(/\\"/g, '"')
    paramstring = JSON.parse(stringfystring)
    tens = `{"action":` + actionName + `,"param":{}}`
    tjson = JSON.parse(tens)
    tjson.param = paramstring
    return tjson
}

// window.dcpeng = window.byted_acrawler.sign
var demo = new Hlclient("ws://127.0.0.1:12080/ws?group=para&name=test");
demo.regAction("get_para", function (resolve, param) {
    console.log(param);
    // var res = dcpeng(param, {"url": "https://www.toutiao.com/?wid=1641423780855"});
    var res = document.cookie
    resolve(res);
})

// 注入hook->瑞数通用
var c = "";
(function() {
    var cookieTemp = "";
    Object.defineProperty(document, 'cookie', {
        set: function(val) {
            console.log('Hook捕获到cookie设置->', val);
            debugger;
            cookieTemp = val;
            c = val;
            return cookieTemp;
        },
        get: function() {
            return cookieTemp;
        }
    });
})();

