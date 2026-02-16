{% macro get_vendor_names(vendor_id_column) %}

{% set vendors = {
    1: 'Creative Mobile Technologies',
    2: 'VeriFone Inc.',
    4: 'Unknown Vendor'
} %}

case {{ vendor_id_column }}
    {% for vendor_id, vendor_name in vendors.items() %}
    when {{ vendor_id }} then '{{ vendor_name }}'
    {% endfor %}
    else 'Unknown'
end

{% endmacro %}