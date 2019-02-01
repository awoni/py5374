"use strict";
$(function() {
  var descriptions = [];
  var areaModels;
  var trash;

  function getSelectedAreaName() {
    return localStorage.getItem("selected_area_name");
  }

  function setSelectedAreaName(name) {
    localStorage.setItem("selected_area_name", name);
  }

  function updateAreaList() {
    $.get("data/area.json", function(data) {
      areaModels = data;
      var row_index = -1
        //エリアとゴミ処理センターを対応後に、表示のリストを生成する。
        //ListメニューのHTML作成
        var selected_name = getSelectedAreaName();
        var area_select_form = $("#select_area");
        var select_html = "";
        select_html += '<option value="-1">地域を選択してください</option>';
        for (var i in areaModels) {
          var area_name = areaModels[i].地名;
          var selected = (selected_name == area_name) ? 'selected="selected"' : "";

          select_html += '<option value="' + i + '" ' + selected + " >" + area_name + "</option>";
        }
        //HTMLへの適応
        area_select_form.html(select_html);
        area_select_form.change();
        // updateData(row_index)
    });
  }

  function createMenuList(after_action) {
    // 備考データを読み込む
    $.get("data/description.json", function(data){
      descriptions = data;
      if (TargetSettings == null) {
        $.get("data/target.json", function (data) {
          for (var i in data) {
            for (var j = 0; j < descriptions.length; j++) {
              //一致してるものに追加する。
              if (descriptions[j].label == data[i].label) {
                descriptions[j].targets.push(data[i]);
                break;
              }
            }
          }
          after_action();
          $("#accordion2").show();
        });
      }
      else{
          after_action();
          $("#accordion2").show();
      }
    });
  }

  function targetHTML(description){
    if (TargetSettings == null) {
      //アコーディオンの分類から対応の計算を行います。
      var target_tag = "";
      var furigana = "";
      var target_tag = "";
      var targets = description.targets;
      for (var j in targets) {
        var target = targets[j];
        if (furigana != target.furigana) {
          if (furigana != "") {
            target_tag += "</ul>";
          }

          furigana = target.furigana;

          target_tag += '<h4 class="initials">' + furigana + "</h4>";
          target_tag += "<ul>";
        }

        target_tag += '<li style="list-style:none;"><div>' + target.name + "</div>";
        target_tag += '<div class="note">' + target.notice + "</div></li>";
      }

      target_tag += "</ul>";
      return target_tag;
    }else{
        //ゴミの分別を index.html から読み込み
        var tg = TargetSettings[description.label];
        return document.getElementById(tg).innerHTML;
    }
  }

  function updateHTML() {
    //SVG が使えるかどうかの判定を行う。
    //TODO Android 2.3以下では見れない（代替の表示も含め）不具合が改善されてない。。
    //参考 http://satussy.blogspot.jp/2011/12/javascript-svg.html
    var ableSVG = (window.SVGAngle !== void 0);
    //var ableSVG = false;  // SVG未使用の場合、descriptionの1項目目を使用
    var accordion_height = $(window).height() / descriptions.length;
    if (descriptions.length > 4) {
      accordion_height = accordion_height / 4.1;
      if (accordion_height > 140) {
        accordion_height = accordion_height / descriptions.length;
      }
      if (accordion_height < 130) {
        accordion_height = 130;
      }
    }
    var styleHTML = "";
    var accordionHTML = "";
    //アコーディオンの分類から対応の計算を行います。
    for (var i in trash) {
      var t = trash[i];

      for (var d_no in descriptions) {
        var description = descriptions[d_no];
        if (description.label != t.label) {
          continue;
        }

        var target_tag = targetHTML(description)

        styleHTML += '#accordion-group' + d_no + '{background-color:  ' + description.bgcolor + ';} ';
        var strs = t.mostRecentText.match(/^\d+-(\d+)-(\d+)/);
        var dateStr = Number(strs[1]) + '月' + Number(strs[2]) + '日';

        accordionHTML +=
            '<div class="accordion-group" id="accordion-group' + d_no + '">' +
            '<div class="accordion-heading">' +
            '<a class="accordion-toggle" style="height:' + accordion_height + 'px" data-toggle="collapse" data-parent="#accordion" href="#collapse' + i + '">' +
            '<div class="left-day">' + t.leftDayText + ' (' + dateStr + ')' + '</div>' +
            '<div class="accordion-table" >';
        if (ableSVG && SVGLabel) {
          accordionHTML += '<img src="' + description.styles + '" alt="' + description.label + '"  />';
        } else {
          accordionHTML += '<p class="text-center">' + description.label + "</p>";
        }
        accordionHTML += "</div>" +
            '<h6><p class="text-left date">' + (t.remark == null ? "" : t.remark) + '<br />' + t.dayLabel + "</p></h6>" +
            "</a>" +
            "</div>" +
            '<div id="collapse' + i + '" class="accordion-body collapse">' +
            '<div class="accordion-inner">' +
            (description.description == null ? "" : description.description) + "<br />" + target_tag +
            '<div class="targetDays"></div></div>' +
            "</div>" +
            "</div>";
      }
    }

    $("#accordion-style").html('<!-- ' + styleHTML + ' -->');

    var accordion_elm = $("#accordion");
    accordion_elm.html(accordionHTML);

    $('html,body').animate({scrollTop: 0}, 'fast');

    //アコーディオンのラベル部分をクリックしたら
    $(".accordion-body").on("shown.bs.collapse", function () {
      var body = $('body');
      var accordion_offset = $($(this).parent().get(0)).offset().top;
      body.animate({
        scrollTop: accordion_offset
      }, 50);
    });
    //アコーディオンの非表示部分をクリックしたら
    $(".accordion-body").on("hidden.bs.collapse", function () {
      if ($(".in").length == 0) {
        $("html, body").scrollTop(0);
      }
    });
  }


  function updateData(row_index) {
    $.get("data/" + areaModels[row_index].収集地区 + ".json", function(data){
      trash = data
      var now = new Date();
      //直近の一番近い日付を計算します。
      for (var i in trash){
        var t = trash[i]
        for (var j in t.dayList) {
          var dt = new Date(t.dayList[j] + "T00:00:00+09:00")
          if (dt - now > -(1000 * 60 * 60 * 24)) {
            t.mostRecentText = t.dayList[j];
            t.mostRecent = dt;
            break;
          }
        }
        //あと何日かを計算する処理です。
        if (t.mostRecent === undefined) {
          t.leftDayText == "不明";
          t.leftDay == 999
        } else {
          t.leftDay = Math.ceil((t.mostRecent.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
          if (t.leftDay == 0) {
            t.leftDayText = "今日";
          } else if (t.leftDay == 1) {
            t.leftDayText = "明日";
          } else if (t.leftDay == 2) {
            t.leftDayText = "明後日"
          } else {
            t.leftDayText = t.leftDay + "日後";
          }
        }
      }

      //トラッシュの近い順にソートします。
      trash.sort(function(a,b){
        return a.leftDay - b.leftDay;
      });

      updateHTML();
    });
  }

  function onChangeSelect(row_index) {　
    if (row_index == -1) {
      $("#accordion").html("");
      setSelectedAreaName("");
      return;
    }
    setSelectedAreaName(areaModels[row_index].地名);

    if ($("#accordion").children().length === 0 && descriptions.length === 0) {

      createMenuList(function() {
        updateData(row_index);
      });
    } else {
      updateData(row_index);
    }
  }

  //リストが選択されたら
  $("#select_area").change(function(data) {
    var row_index = $(data.target).val();
    onChangeSelect(row_index);
  });

  updateAreaList();
});
