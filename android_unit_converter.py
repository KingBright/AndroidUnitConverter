#!/usr/bin/python
# -*- coding: UTF-8 -*-

import xml.sax

BASE_DPI = 160

OPTIONS = {'ldpi': 120, 'mdpi': 160, 'hdpi': 240, 'xhdpi': 320, 'xxhdpi': 480, 'xxxhdpi': 640}


# dpi描述类
class DpiOption:
    def __init__(self, name, value):
        self.name = name
        self.value = value


# 转换结果描述
class ConvertResult:
    def __init__(self, name, cate, unit, value):
        self.name = name
        self.cate = cate
        self.unit = unit
        self.value = value


# convert px to dp
class AndroidUnitConvert:
    def __init__(self):
        super().__init__()
        self.scale = 1.0
        self.sourceDpiOption = None
        self.optionList = []
        self.unitList = []
        for (k, v) in OPTIONS.items():
            option = DpiOption(k, v)
            self.optionList.append(option)

    def setSourceDpiOption(self, dpi):
        self.sourceDpiOption = dpi
        return self

    def setSpScale(self, scale):
        self.scale = scale
        return self

    # convert px to dp for one value and print out in terminal
    def convertValue(self, idName, val, printLog):
        px = int(val)
        d = self.sourceDpiOption.value
        result = []
        for option in self.optionList:
            row_dp = option.value
            if row_dp == 0:
                continue
            if d == 0:
                dp = val / (row_dp / BASE_DPI)
            else:
                dp = px * BASE_DPI / row_dp

            # perform scale compensation
            sp = dp / self.scale

            dpv = round(dp, 2)
            result.append(ConvertResult(idName, option.name, "dp", dpv))
            if printLog:
                print("convert", val, "px to", dpv, "dp for", idName, "at", option.name)

                # don't use currently
                # pxv = px.toFixed(2) + "px"
                # spv = sp.toFixed(2) + "sp"
        return result

    def convertFile(self, filepath):
        # 创建一个 XMLReader
        parser = xml.sax.make_parser()
        handler = ResourceHandler()
        handler.setHandleCallback(self.convertValue)
        handler.setFinishCallback(self.__generateFile)
        parser.setContentHandler(handler)
        parser.parse(filepath)

    def __generateFile(self, result):
        lists = {}
        for v in result:
            if lists.get(v.cate, None) is None:
                lists[v.cate] = []
            lists[v.cate].append(v)

        for k, v in lists.items():
            print("current dpi is", k)
            for item in lists[k]:
                print("<dimen name=\"%s\">%d%s</dimen>" % (item.name, item.value, item.unit))


class ResourceHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.handleCallback = None
        self.finishCallback = None
        self.currentTag = None
        self.currentId = None
        self.result = None

    # 元素开始事件处理
    def startElement(self, tag, attributes):
        if tag == "resources":
            self.result = []
        if tag == "dimen":
            self.currentTag = tag
            self.currentId = attributes["name"]
        else:
            self.currentTag = None
            self.currentId = None

    # 元素结束事件处理
    def endElement(self, tag):
        self.currentId = None
        self.currentTag = None
        if tag == "resources":
            if self.finishCallback is not None:
                self.finishCallback(self.result)

    # 内容事件处理
    def characters(self, content):
        if self.currentId is None or self.currentId == "":
            return
        if self.currentTag is None or self.currentTag == "":
            return
        if content is None or content == "":
            return
        if content.endswith("px"):
            if self.handleCallback is not None:
                parts = content.partition("px")
                result = self.handleCallback(self.currentId, parts[0], False)
                if self.result is not None:
                    self.result.extend(result)

    def setHandleCallback(self, callback):
        self.handleCallback = callback

    def setFinishCallback(self, callback):
        self.finishCallback = callback


if __name__ == "__main__":
    convert = AndroidUnitConvert()
    convert.setSpScale(1)
    convert.setSourceDpiOption(DpiOption("xhdpi", 320))

    # convert.convertValue("test", 100, True)

    convert.convertFile("/your/path/to/dimens.xml")
