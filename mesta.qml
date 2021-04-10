import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQml.Models 2.1
import QtLocation 5.6
import QtPositioning 5.6

Row {
    id: vsecko
    width: 1000
    height: 600

    property var currentModelItem

    Column{
    ListView {
        height: 50
        width: 100
        model: ["Města"]
        delegate: CheckDelegate {
            id:checkbox
            text: modelData
            onToggled: function() { 
            if (checkState === Qt.Checked) 
                cityListModel.truemesto()
            else
                cityListModel.falsemesto()
            }
        }
    }

    ListView {
        height: 50
        width: 100
        model: ["Obce"]
        delegate: CheckDelegate {
            text: modelData
            onToggled: function() { 
            if (checkState === Qt.Checked) 
                cityListModel.trueobec()
            else
                cityListModel.falseobec()
            }
        }
    }

    Text {
        height: 30
        width: 100
        text: 'Počet obyvatel: '
        horizontalAlignment: Text.AlignVCenter
    }

    RangeSlider {
            id:posuvnik
            from: 0
            to: 1400000
            first.value: cityListModel.dolni
            second.value: cityListModel.horni
                Binding{
                    target: cityListModel
                    property: "dolni"
                    value: posuvnik.first.value
                    }
                Binding{
                    target: cityListModel
                    property: "horni"
                    value: posuvnik.second.value
                    }
            }

    Item{
        width: 135
        height: 30

    Text {
        width: 20
        height: 30
        text: 'Od: '
        horizontalAlignment: Text.AlignVCenter
    }
    TextInput {
                id: doInput
                x: 25
                y: 0
                width: 45
                height: 30
                maximumLength: 6
                text: cityListModel.dolni
                Binding{
                    target: cityListModel
                    property: "dolni"
                    value: doInput.text
                    }
            }
    Text {
        x: 75
        y: 0
        width: 20
        height: 30
        text: 'Do: '
        horizontalAlignment: Text.AlignVCenter
    }

    TextInput {
                id: odInput
                x: 100
                y: 0
                width: 55
                height: 30
                maximumLength: 7
                text: cityListModel.horni
                Binding{
                    target: cityListModel
                    property: "horni"
                    value: odInput.text
                    }
            }
    }
        Text {
        width: 20
        height: 30
        text: 'Kraj:'
        horizontalAlignment: Text.AlignVCenter
    }
    ComboBox {
    id:krajeList
    width: 200
    focus: true
    selectTextByMouse: true
    textRole: "display"
    onHighlighted: krajeList.currentIndex = index
    onActivated: krajeList.currentIndex = index
    Binding{
        target: krajeListModel
        property: "krajus"
        value: krajeList.currentText
        }
    delegate: ItemDelegate {
        text: model.display
        width: parent.width
        onClicked: {krajeList.currentIndex = index
        krajeListModel.zmena()
        okresyListModel.filtr()
        vsecko.forceLayout()
        }
    }


        model: DelegateModel {
            id: krajeListDelegateModel
            model: krajeListModel
            delegate: krajeListDelegate
        }


    }
    Text {
        width: 20
        height: 30
        text: 'Okres:'
        horizontalAlignment: Text.AlignVCenter
    }
    ComboBox {
    id:okresyList
    width: 200
    focus: true
    selectTextByMouse: true
    textRole: "display"
    onHighlighted: okresyList.currentIndex = index
    onActivated: okresy.currentIndex = index
    Binding{
        target: cityListModel
        property: "okres"
        value: okresyList.currentText
        }
    delegate: ItemDelegate {
        id: delegatek
        text: model.display
        width: parent.width
        onClicked: okresyList.currentIndex = index
    }


        model: DelegateModel {
            id: okresyListDelegateModel
            model: okresyListModel
            delegate: okresyListDelegate
        }


    }
    Text {
        width: 20
        height: 30
        text: ''
        horizontalAlignment: Text.AlignVCenter
    }

                Button {
                width: 200
                id: filtrovat
                text: qsTr("Filtrovat!")
                onClicked: {cityListModel.filtrovani()
                            vsecko.forceLayout()
                            mapka.removeMapItemView(popisky)
                            mapka.addMapItemView(popisky)}
            }
    }
    

    ListView {
        id: cityList
        focus: true
        height: 300
        width: 200


        Component {
            id: cityListDelegate
            Item {
                width: parent.width
                height: childrenRect.height
                Text {
                    text: model.display
                    textFormat: Text.RichText
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: cityList.currentIndex = index
                }
            }
        }

        model: DelegateModel {
            id: cityListDelegateModel
            model: cityListModel
            delegate: cityListDelegate
        }

        onCurrentItemChanged: currentModelItem = cityListDelegateModel.items.get(cityList.currentIndex).model 

        highlight: Rectangle {
            color: "lightsteelblue"
        }

    }
    Column {
        Text {
            text: 'Název: '+ currentModelItem.display
        }
        Text {
            text: 'Počet obyvatel: ' + currentModelItem.population
        }
        Text {
            text: 'Rozloha: ' + currentModelItem.area + 'km<sup>2</sup>'
            textFormat: Text.RichText
        }

    }
    Plugin {
        id: osmPlugin
        name: "osm"
        PluginParameter {
            name: "osm.mapping.custom.host"
            value: "https://tiles.wmflabs.org/osm-no-labels/"
        }

    }
    Map {
        id:mapka
        height: 500
        width: 500

        center: currentModelItem.location
        zoomLevel: 12

        plugin: osmPlugin
        activeMapType: supportedMapTypes[supportedMapTypes.length - 1]

    MapItemView {
            id:popisky
            model: cityListModel
            delegate: MapQuickItem {
                    coordinate: model.location
                    sourceItem: Text {text: model.display}

            }
        }

    }
}