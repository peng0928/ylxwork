var argument = {
    "0": "/api/charts/getequityinvestment"
};
o = {
    'default': {
        'codes': {
            "0": "W",
            "1": "l",
            "2": "k",
            "3": "B",
            "4": "Q",
            "5": "g",
            "6": "f",
            "7": "i",
            "8": "i",
            "9": "r",
            "10": "v",
            "11": "6",
            "12": "A",
            "13": "K",
            "14": "N",
            "15": "k",
            "16": "4",
            "17": "L",
            "18": "1",
            "19": "8"
        },
        'n': 20,
    }
};
function r(e) {

    for (e.toLowerCase(),
             t = e + e, n = "", i = 0; i < t.length; ++i) {

        var a = t[i].charCodeAt() % o.default.n;
        n += o.default.codes[a];

    }
    return n
};
e = "/api/datalist/touzilist?keyno=abc50fc7ac1d549540f6339b22d60aad&pageindex=4"
//父级 '/api/charts/getownershipstructuremix{"keyno":"8c9f7ddc1a7bcee3d1f7676773fe9404","level":1}'
//父级 '/api/charts/getownershipstructuremixpathString{"keyno":"8c9f7ddc1a7bcee3d1f7676773fe9404","level":1}a2f9c4e1d81e4887c0e08ff013acf07f'
aaa = r(e);
console.log('touzilist:',aaa);


e = "/api/charts/getequityinvestment"
//父级 '/api/charts/getequityinvestment{"keyno":"8c9f7ddc1a7bcee3d1f7676773fe9404"}'
//父级 '/api/charts/getownershipstructuremixpathString{"keyno":"8c9f7ddc1a7bcee3d1f7676773fe9404","level":1}a2f9c4e1d81e4887c0e08ff013acf07f'
aaa = r(e);
console.log('getequityinvestment:', aaa);

