import argparse
import csv
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


def get_nested(data, *paths, default=None):
    for path in paths:
        current = data
        try:
            for key in path:
                current = current[key]
            if current is not None:
                return current
        except (KeyError, TypeError):
            continue
    return default


def to_decimal(value):
    if value in (None, ""):
        return Decimal("0")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def classify_operation(dte, nit_contribuyente):
    if not nit_contribuyente:
        return "sin_clasificar"

    emisor_nit = get_nested(dte, ("emisor", "nit"), default="")
    receptor_nit = get_nested(dte, ("receptor", "nit"), default="")
    nit = nit_contribuyente.replace("-", "").strip()

    if str(emisor_nit).replace("-", "").strip() == nit:
        return "venta"
    if str(receptor_nit).replace("-", "").strip() == nit:
        return "compra"
    return "tercero"


def normalize_record(dte, source_file, nit_contribuyente):
    identificacion = dte.get("identificacion", {})
    resumen = dte.get("resumen", {})

    total_exenta = to_decimal(
        get_nested(
            dte,
            ("resumen", "totalExenta"),
            ("resumen", "totalExentas"),
            default=0,
        )
    )
    total_no_sujeta = to_decimal(
        get_nested(
            dte,
            ("resumen", "totalNoSuj"),
            ("resumen", "totalNoSujeta"),
            default=0,
        )
    )
    total_gravada = to_decimal(
        get_nested(
            dte,
            ("resumen", "totalGravada"),
            ("resumen", "totalGravadas"),
            ("resumen", "subTotalVentas"),
            default=0,
        )
    )
    iva = to_decimal(
        get_nested(
            dte,
            ("resumen", "totalIva"),
            ("resumen", "ivaPerci1"),
            ("resumen", "ivaRete1"),
            default=0,
        )
    )
    total_operacion = to_decimal(
        get_nested(
            dte,
            ("resumen", "montoTotalOperacion"),
            ("resumen", "totalPagar"),
            default=0,
        )
    )

    return {
        "fecha_emision": get_nested(
            dte,
            ("identificacion", "fecEmi"),
            ("identificacion", "fechaEmision"),
            default="",
        ),
        "tipo_dte": identificacion.get("tipoDte", ""),
        "numero_control": identificacion.get("numeroControl", ""),
        "codigo_generacion": identificacion.get("codigoGeneracion", ""),
        "sello_recibido": get_nested(
            dte,
            ("respuestaHacienda", "selloRecibido"),
            ("selloRecibido",),
            default="",
        ),
        "emisor_nit": get_nested(dte, ("emisor", "nit"), default=""),
        "emisor_nrc": get_nested(dte, ("emisor", "nrc"), default=""),
        "receptor_nit": get_nested(dte, ("receptor", "nit"), default=""),
        "receptor_nrc": get_nested(dte, ("receptor", "nrc"), default=""),
        "total_exenta": f"{total_exenta:.2f}",
        "total_no_sujeta": f"{total_no_sujeta:.2f}",
        "total_gravada": f"{total_gravada:.2f}",
        "iva": f"{iva:.2f}",
        "total_operacion": f"{total_operacion:.2f}",
        "tipo_operacion": classify_operation(dte, nit_contribuyente),
        "archivo_origen": source_file,
        "_totals": {
            "total_exenta": total_exenta,
            "total_no_sujeta": total_no_sujeta,
            "total_gravada": total_gravada,
            "iva": iva,
            "total_operacion": total_operacion,
        },
    }


def load_dte_files(input_dir):
    records = []
    errors = []
    for file_path in sorted(input_dir.glob("*.json")):
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            records.append((file_path.name, data))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({"archivo": file_path.name, "error": str(exc)})
    return records, errors


def write_csv(records, output_csv):
    fieldnames = [
        "fecha_emision",
        "tipo_dte",
        "numero_control",
        "codigo_generacion",
        "sello_recibido",
        "emisor_nit",
        "emisor_nrc",
        "receptor_nit",
        "receptor_nrc",
        "total_exenta",
        "total_no_sujeta",
        "total_gravada",
        "iva",
        "total_operacion",
        "tipo_operacion",
        "archivo_origen",
    ]
    with output_csv.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(row)


def write_summary(records, errors, summary_file):
    grouped = defaultdict(
        lambda: {
            "documentos": 0,
            "total_exenta": Decimal("0"),
            "total_no_sujeta": Decimal("0"),
            "total_gravada": Decimal("0"),
            "iva": Decimal("0"),
            "total_operacion": Decimal("0"),
        }
    )

    for record in records:
        op = record["tipo_operacion"]
        grouped[op]["documentos"] += 1
        for key, value in record["_totals"].items():
            grouped[op][key] += value

    summary = {
        "totales_por_tipo_operacion": {
            op: {
                "documentos": data["documentos"],
                "total_exenta": f"{data['total_exenta']:.2f}",
                "total_no_sujeta": f"{data['total_no_sujeta']:.2f}",
                "total_gravada": f"{data['total_gravada']:.2f}",
                "iva": f"{data['iva']:.2f}",
                "total_operacion": f"{data['total_operacion']:.2f}",
            }
            for op, data in grouped.items()
        },
        "errores_lectura": errors,
    }

    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Lee archivos DTE JSON de El Salvador y genera un archivo CSV "
            "de apoyo para declaración de IVA."
        )
    )
    parser.add_argument(
        "--input-dir",
        default=r"C:\dte",
        help="Carpeta con archivos DTE en formato JSON (por defecto: C:\\dte).",
    )
    parser.add_argument(
        "--output-csv",
        default="iva_declaracion.csv",
        help="Ruta del CSV de salida para declaración de IVA.",
    )
    parser.add_argument(
        "--output-summary",
        default="iva_resumen.json",
        help="Ruta del resumen de totales y errores.",
    )
    parser.add_argument(
        "--nit-contribuyente",
        default="",
        help=(
            "NIT del contribuyente para clasificar automáticamente "
            "documentos como venta/compra."
        ),
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_csv = Path(args.output_csv)
    summary_file = Path(args.output_summary)

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"La carpeta de entrada no existe: {input_dir}")

    dte_items, errors = load_dte_files(input_dir)
    records = [
        normalize_record(dte, source_file, args.nit_contribuyente)
        for source_file, dte in dte_items
    ]

    write_csv(records, output_csv)
    write_summary(records, errors, summary_file)

    print(f"Documentos procesados: {len(records)}")
    print(f"CSV generado: {output_csv.resolve()}")
    print(f"Resumen generado: {summary_file.resolve()}")
    if errors:
        print(f"Archivos con error: {len(errors)} (ver resumen)")


if __name__ == "__main__":
    main()
