from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QWidget,
    QDateEdit,
    QMessageBox,
    QLineEdit,
    QTabWidget,
    QLabel,
    QTreeWidgetItem,
    QTreeWidget,
    QSpinBox,
    QHBoxLayout,
)
from PyQt5 import uic
from PyQt5.QtCore import QDate


from controllers.presupuesto_controller import (
    save_current_presupuesto,
    search_empresa,
    load_all_presupuestos,
)

time = QDate.currentDate()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)

        # Encontramos el QStackedWidget
        self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")

        self.tab_widget = self.findChild(QTabWidget, "first_tab")
        self.btn_add_tab = self.findChild(QPushButton, "btn_add_tab")
        self.btn_add_tab.clicked.connect(self.add_new_tab)

        # Conectar los botones del menú con las vistas
        self.btn_presupuesto = self.findChild(QPushButton, "btn_presupuesto")
        self.btn_resumen = self.findChild(QPushButton, "btn_resumen")
        self.btn_factura = self.findChild(QPushButton, "btn_factura")
        self.btn_guardar = self.findChild(QPushButton, "btn_guardar")
        self.btn_buscar_empresa = self.findChild(QPushButton, "btn_buscar_empresa")
        self.btn_buscar_empresa.clicked.connect(lambda: search_empresa(self))
        self.btn_guardar.clicked.connect(lambda: save_current_presupuesto(self))
        self.date_value = self.findChild(QDateEdit, "input_fecha")
        self.date_value.setDate(time)

        self.date_search = self.findChild(QDateEdit, "input_search_date")
        self.date_search.setDate(time)
        self.tree_widget = self.findChild(QTreeWidget, "treeWidget")
        self.setup_treewidget(self.tree_widget)
        self.load_presupuestos()

        self.btn_presupuesto.clicked.connect(self.show_presupuesto)
        self.btn_resumen.clicked.connect(self.show_resumen)
        self.btn_factura.clicked.connect(self.show_factura)

        self.connect_fields(self.tab_widget.widget(0))

    def add_new_tab(self):

        index = self.tab_widget.count()
        new_tab = QWidget()
        uic.loadUi("ui/tab_template.ui", new_tab)

        tab_index = self.tab_widget.count() + 1
        self.tab_widget.addTab(new_tab, f"Etapa {tab_index}")
        self.tab_widget.setCurrentWidget(new_tab)

        for child in new_tab.findChildren(QWidget):
            print(f"Widget encontrado: {child.objectName()}")

        self.connect_fields(new_tab)

        close_button = QPushButton("x")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(lambda: self.remove_tab(index))

        tab_label = QLabel(f"Etapa {tab_index+1}")
        self.tab_widget.tabBar().setTabButton(
            index, self.tab_widget.tabBar().RightSide, close_button
        )

    def remove_tab(self, index):

        if self.tab_widget.count() > 1:

            self.tab_widget.removeTab(index)
            input_subtotal = self.stacked_widget.findChild(QLineEdit, "input_subtotal")
            input_total = self.stacked_widget.findChild(QLineEdit, "input_total")
            if input_subtotal:
                input_subtotal.setText("0.00")
            if input_total:
                input_total.setText("0.00")
            self.update_totals()
        else:
            QMessageBox.warning(self, "Error", "No se puede eliminar la última etapa")

    def connect_fields(self, tab):

        cantidad = tab.findChild(QSpinBox, "input_cantidad")
        precio = tab.findChild(QLineEdit, "input_precio")
        descuento = tab.findChild(QLineEdit, "input_descuento")
        importe = tab.findChild(QLineEdit, "input_importe")
        subtotal = self.stacked_widget.findChild(QLineEdit, "input_subtotal")

        iva_field = self.stacked_widget.findChild(QLineEdit, "input_iva")
        if iva_field:
            iva_field.textChanged.connect(self.update_totals)

        cantidad.valueChanged.connect(
            lambda: self.update_subtotal(cantidad, precio, descuento, subtotal, importe)
        )
        precio.textChanged.connect(
            lambda: self.update_subtotal(cantidad, precio, descuento, subtotal, importe)
        )
        descuento.textChanged.connect(
            lambda: self.update_subtotal(cantidad, precio, descuento, subtotal, importe)
        )

    def update_subtotal(self, cantidad, precio, descuento, subtotal, importe):
        try:

            precio_val = float(precio.text()) if precio.text() else 0
            descuento_val = float(descuento.text()) / 100 if descuento.text() else 0

            importe.setText(
                f"{cantidad.value() * float(precio_val) * (1 - float(descuento_val) ):.2f}"
            )

            self.update_totals()

        except ValueError:
            QMessageBox.warning(self, "Error", "Verifique los valores ingresados")
            subtotal.setText("0.00")
            return

    def update_totals(self):

        subtotal_general = 0

        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            input_importe = tab.findChild(QLineEdit, "input_importe")

            if input_importe and input_importe.text():
                try:
                    subtotal_general += float(input_importe.text())
                except ValueError:
                    QMessageBox.warning(
                        self, "Error", "Verifique los valores ingresados"
                    )
                    return
        self.stacked_widget.findChild(QLineEdit, "input_subtotal").setText(
            f"{subtotal_general:.2f}"
        )

        iva_field = self.stacked_widget.findChild(QLineEdit, "input_iva")
        iva_val = float(iva_field.text()) / 100 if iva_field.text() else 0
        iva_final = subtotal_general * iva_val

        print(f"IVA: {iva_val}")

        total_final = float(subtotal_general) + float(iva_final)
        self.stacked_widget.findChild(QLineEdit, "input_total").setText(
            f"{total_final:.2f}"
        )

    def show_presupuesto(self):
        # Cambiar al primer widget en el stacked widget
        self.stacked_widget.setCurrentIndex(0)

    def show_resumen(self):
        # Cambiar al segundo widget en el stacked widget
        self.stacked_widget.setCurrentIndex(1)

    def setup_treewidget(self, tree_widget):
        tree_widget.setColumnCount(4)
        tree_widget.setHeaderLabels(
            [
                "Nombre Empresa",
                "Nombre Presupuesto",
                "Fecha",
                "Acciones",
            ]
        )
        tree_widget.setIndentation(15)

    def add_empresa(self, tree_widget, nombre_empresa):
        empresa_item = QTreeWidgetItem(tree_widget)
        empresa_item.setText(0, nombre_empresa)
        empresa_item.setExpanded(True)
        return empresa_item

    def add_presupuesto(self, parent, nombre_presupuesto, fecha):
        presupuesto_item = QTreeWidgetItem(parent)
        presupuesto_item.setText(1, nombre_presupuesto)
        presupuesto_item.setText(2, fecha)

        widget = QWidget()
        layout = QHBoxLayout()

        btn_editar = QPushButton("✏️")
        btn_detalles = QPushButton("🔍")
        btn_descargar = QPushButton("⬇️")
        btn_imprimir = QPushButton("🖨️")

        layout.addWidget(btn_editar)
        layout.addWidget(btn_detalles)
        layout.addWidget(btn_descargar)
        layout.addWidget(btn_imprimir)

        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        parent.treeWidget().setItemWidget(presupuesto_item, 3, widget)

        return presupuesto_item

    def load_presupuestos(
        self,
    ):
        self.tree_widget.clear()
        load_all_presupuestos(self)

        datos = {
            "Empresa X": [
                {"presupuesto": "Presupuesto A", "fecha": "2025-02-16"},
                {"presupuesto": "Presupuesto B", "fecha": "2025-02-15"},
            ],
            "Empresa Y": [
                {"presupuesto": "Presupuesto C", "fecha": "2025-02-14"},
                {"presupuesto": "Presupuesto D", "fecha": "2025-02-13"},
            ],
        }
        for empresa, presupuestos in datos.items():
            empresa_item = self.add_empresa(self.tree_widget, empresa)
            for presupuesto in presupuestos:
                self.add_presupuesto(
                    empresa_item, presupuesto["presupuesto"], presupuesto["fecha"]
                )

    def show_factura(self):
        # Cambiar al tercer widget en el stacked widget
        self.stacked_widget.setCurrentIndex(2)
