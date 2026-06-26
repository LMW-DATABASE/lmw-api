MOLECULE_RANGE_FILTER_FIELDS = {
    'mw_average': float,
    'mw_exact': float,
    'logp': float,
    'tpsa': float,
    'h_bond_donors': int,
    'h_bond_acceptors': int,
    'heavy_atom_count': int,
    'rotatable_bonds': int,
    'ring_count': int,
    'aromatic_ring_count': int,
    'fraction_csp3': float,
    'qed_score': float,
    'np_likeness_score': float,
}


def _parse_range_value(raw, cast_type):
    if raw is None or raw == '':
        return None
    try:
        return cast_type(raw)
    except (TypeError, ValueError):
        return None


def apply_molecule_range_filters(queryset, params):
    for field_name, cast_type in MOLECULE_RANGE_FILTER_FIELDS.items():
        min_key = f'{field_name}_min'
        max_key = f'{field_name}_max'
        min_val = _parse_range_value(params.get(min_key), cast_type)
        max_val = _parse_range_value(params.get(max_key), cast_type)

        if min_val is None and max_val is None:
            continue

        if min_val is not None and max_val is not None and min_val > max_val:
            continue

        queryset = queryset.filter(**{f'{field_name}__isnull': False})

        if min_val is not None:
            queryset = queryset.filter(**{f'{field_name}__gte': min_val})
        if max_val is not None:
            queryset = queryset.filter(**{f'{field_name}__lte': max_val})

    return queryset
