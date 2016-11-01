from etaprogress.components.units import UnitByte


def humanize_bytes(bytes):
    unit_numerator, unit = UnitByte(bytes).auto
    return '{:.2f} {}'.format(unit_numerator, unit)

