from models.database import (
    save_presupuesto,
    get_or_create_empresa,
    get_presupuestos_by_empresa,
    get_connection,
)
from PyQt5.QtWidgets import (
    QMessageBox,
    QLineEdit,
    QSpinBox,
    QDateEdit,
    QTextEdit,
    QTreeWidgetItem,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QTreeWidget,
)


def save_current_presupuesto(main_window):
    empresa_nombre = main_window.findChild(QLineEdit, "input_empresa").text().strip()
    nombre_presupuesto = (
        main_window.findChild(QLineEdit, "input_nombre_presupuesto").text().strip()
    )
    fecha_widget = main_window.findChild(QDateEdit, "input_fecha")
    fecha = fecha_widget.date().toString("dd/MM/yy")

    if not empresa_nombre or not nombre_presupuesto or not fecha:
        QMessageBox.warning(main_window, "Error", "Todos los campos deben estar llenos")
        return

    subtotal = float(main_window.findChild(QLineEdit, "input_subtotal").text() or 0)
    iva = float(main_window.findChild(QLineEdit, "input_iva").text() or 0)
    total = float(main_window.findChild(QLineEdit, "input_total").text() or 0)

    etapas = []
    for index in range(main_window.tab_widget.count()):
        tab = main_window.tab_widget.widget(index)
        cantidad = tab.findChild(QSpinBox, "input_cantidad").value()
        precio = float(tab.findChild(QLineEdit, "input_precio").text() or 0)
        if cantidad <= 0 or precio <= 0:
            QMessageBox.warning(
                main_window, "Error", "Cantidad o Precio no pueden ser 0 o menor."
            )
        etapas.append(
            {
                "etapa": index + 1,
                "descripcion": tab.findChild(QTextEdit, "input_descripcion")
                .toPlainText()
                .strip(),
                "cantidad": cantidad,
                "precio": precio,
                "descuento": float(
                    tab.findChild(QLineEdit, "input_descuento").text() or 0
                ),
                "importe": float(tab.findChild(QLineEdit, "input_importe").text() or 0),
            }
        )

    save_presupuesto(
        empresa_nombre, nombre_presupuesto, fecha, subtotal, iva, total, etapas
    )
    QMessageBox.information(main_window, "Éxito", "Presupuesto guardado correctamente")
    clear_fields(main_window)


def clear_fields(main_window):
    main_window.input_empresa.clear()
    main_window.input_nombre_presupuesto.clear()
    main_window.input_subtotal.setText("0.00")
    main_window.input_iva.setText("0.00")
    main_window.input_total.setText("0.00")
    while main_window.tab_widget.count() > 1:
        main_window.tab_widget.removeTab(1)


def search_empresa(main_window):
    empresa_nombre = main_window.findChild(QLineEdit, "input_empresa").text().strip()

    if not empresa_nombre:
        QMessageBox.warning(main_window, "Error", "Debe ingresar un nombre de empresa")
        return

    empresa_id = get_or_create_empresa(empresa_nombre)
    print(empresa_id)
    main_window.input_empresa.setText(f"{empresa_id} - {empresa_nombre}")


def load_all_presupuestos(main_window):
    tree_widget = main_window.findChild(QTreeWidget, "treeWidget")
    tree_widget.clear()

    # Obtener todas las empresas con sus presupuestos
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre FROM empresas")
    empresas = cursor.fetchall()

    for empresa_id, nombre_empresa in empresas:
        empresa_item = QTreeWidgetItem(tree_widget)
        empresa_item.setText(0, nombre_empresa)
        empresa_item.setExpanded(True)

        # Obtener los presupuestos de esta empresa
        cursor.execute(
            "SELECT id, nombre, fecha FROM presupuestos WHERE empresa_id = ?",
            (empresa_id,),
        )
        presupuestos = cursor.fetchall()

        for presupuesto_id, nombre_presupuesto, fecha in presupuestos:
            presupuesto_item = QTreeWidgetItem(empresa_item)
            presupuesto_item.setText(1, nombre_presupuesto)
            presupuesto_item.setText(2, fecha)

            # Agregar botones de acción
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

            tree_widget.setItemWidget(presupuesto_item, 3, widget)

    conn.close()


def search_presupuestos(main_window):

    tree_widget = main_window.findChild(QTreeWidget, "treeWidget")
    search_text = main_window.findChild(QLineEdit, "input_search_name")
    conn = get_connection()
    cursor = conn.cursor()

    tree_widget.clear()

    if not search_text:
        load_all_presupuestos(main_window)

    cursor.execute(
        "SELECT id, nombre FROM empresas WHERE nombre LIKE ?", (f"%{search_text}%",)
    )
    empresas = cursor.fetchall()

    if empresas:
        for empresa_id, nombre_empresa in empresas:
            empresa_item = QTreeWidgetItem(tree_widget)
            empresa_item.setText(0, nombre_empresa)
            empresa_item.setExpanded(True)

            cursor.execute(
                "SELECT id, nombre, fecha FROM presupuestos WHERE empresa_id = ?",
                (empresa_id,),
            )
