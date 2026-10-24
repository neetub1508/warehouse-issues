#!/usr/bin/env python3
"""P7-12 (#560) G11 - the 20-warehouse.def ledger check.

Usage: python3 tools/check-ci-def.py <classic-root>   -> exit 0 and prints nothing when clean.

1. Every test class the def names (simple or fully-qualified, `$Nested` stripped, `Foo(Bar)BazTest` shorthand
   expanded to both spellings) exists as a source file under a warehouse* or platform test tree. A `*`-prefixed
   family (`*IntegrationTest`) is not a class and is skipped; an all-caps word ending in IT/Test (EXIT, LIMIT,
   ADMIT, IN_TRANSIT, W53_COMMIT) is not a class token.
2. Every `Class#method` / `Class.method` the def names exists in that class's file - a class check alone cannot see
   a deleted method in a kept class.
3. FRD-REM §6 GATE-1/2/3/5 and contract §1.7 RMV-UNR-01..13 (with the RMV-UNR-10 extension) print nothing over the
   def: no exemption, D-16 notes included (RMV-UNR-24).
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
DEF = os.path.join(ROOT, 'shared/scripts/ci-gate/20-warehouse.def')
TREES = ['warehouse-base', 'warehouse', 'warehouse-3pl', 'warehouse-india', 'platform']

GATES = {
    'GATE-1': r'WhAwb|AwbPool|ShipmentNdr|WhNdr|CodRemittance|WhCod[A-Z]|ChannelAccount|ChannelOrderImport|ChannelPublish|TrackingLink|TrackingNotification|TrackingPublic|MarketplaceClaim|RtoConsignment|RtoReceipt|CarrierServiceability|RateQuote|RateShop|ObsolescenceReturn|ObsolescenceCandidate|ObsolescenceWindow|TradePortal|TradeCustomer|CustomerPersona|Coexistence|CategoryStockingOwnership|ExternalStockSnapshot|StockingSystem|ConsolidatedValuation|InventorySeparation|PartsKpi|partsKpi',
    'GATE-2': r'wh_awb_|wh_shipment_ndrs|wh_ndr_actions|wh_cod_remittance|wh_channel_account|wh_channel_order_import|wh_channel_publish|wh_tracking_link|wh_tracking_notification|wh_marketplace_claim|wh_rto_consignment|wh_carrier_serviceability|wh_rate_quote|wh_obsolescence_return|wh_trade_portal|whb_category_stocking_ownership|whb_external_stock_snapshot|wh_rpt_coexistence|wh_rpt_consolidated_valuation|wh_rpt_parts_kpis|is_dual_eligible|isDualEligible|supports_cod|supportsCod',
    'GATE-3': r"ADAPTER_(DEALER|SERVICES|FIELD_SERVICE|ASSETS)|'ACCESSORIES'|\"ACCESSORIES\"|JOB_CARD|POS_SHIFT|MARKETPLACE_LISTING|CHANNEL_PUBLISH_RUN|CHANNEL_ORDER_ID|RTO_RECEIPT|RTO_INITIATED|RTO_IN_TRANSIT|RTO_DELIVERED|NDR_[A-Z_]+|CARRIER_INITIATED|AWB_VOID|OWN_STORE|OBSOLESCENCE_RETURN|TYPE_OBSOLESCENCE|OEM_PART_NUMBER|\bPAYMENT_MODE\b|DO_PAYMENT_MODE|DO_COD_AMOUNT|PAYMENT_(PREPAID|COD)\b|WhDemandOrder\.PAYMENT_MODES|channel\.inventory\.published",
    'GATE-5': r'outbound/(awb-pools|ndr|cod-remittances|channel-accounts|channel-imports|publish-rules|tracking-links|rto|serviceability|rate-quotes|trade-portal)|inbound/(obsolescence-returns|marketplace-claims)|reports/(coexistence|consolidated-valuation|parts-kpis)|masters/category-ownership|platform/external-snapshots|/public/warehouse',
    'RMV-UNR-01': r'WhAwb|AwbPool|wh_awb_|AWB_VOID|SHIPMENT_TRACKING_NOT_CLAIMED_AWB|WAREHOUSE_AWB_POOL_LOW|WH_AWB_POOL_TOP_UP|outbound/awb-pools',
    'RMV-UNR-02': r'CarrierServiceability|RateQuote|RateShop|wh_carrier_serviceability|wh_rate_quote|WH_CARRIER_SERVICEABILITY|outbound/(serviceability|rate-quotes)|fetchAwbBlock',
    'RMV-UNR-03': r'ShipmentNdr|WhNdr|wh_shipment_ndrs|wh_ndr_actions|WH_NDR_|WAREHOUSE_NDR|RTO_INITIATED|RTO_IN_TRANSIT|RTO_DELIVERED|ndr_response_hours|ndr_auto_rto_grace_hours|outbound/ndr',
    'RMV-UNR-04': r'CodRemittance|WhCod[A-Z]|wh_cod_remittance|cod_remittance_days|supports_cod|supportsCod|DO_PAYMENT_MODE|DO_COD_AMOUNT|PAYMENT_(PREPAID|COD)\b|WhDemandOrder\.PAYMENT_MODES|outbound/cod-remittances',
    'RMV-UNR-05': r'ChannelAccount|ChannelOrderImport|ChannelPublish|wh_channel_account|wh_channel_order_import|wh_channel_publish|channel\.inventory\.published|CHANNEL_PUBLISH_RUN|CHANNEL_ORDER_ID|channel_account_id|dropdown\.whChannel|outbound/(channel-accounts|channel-imports|publish-rules)',
    'RMV-UNR-06': r'TrackingLink|TrackingNotification|TrackingPublic|wh_tracking_link|wh_tracking_notification|/public/warehouse|outbound/tracking-links',
    'RMV-UNR-07': r'MarketplaceClaim|wh_marketplace_claim|MARKETPLACE_CLAIM_TYPE|warehouse\.marketplace_claims|WH_MARKETPLACE_CLAIM_WINDOW|WhClaimSettlementRequest|inbound/marketplace-claims',
    'RMV-UNR-08': r'RtoConsignment|RtoReceipt|wh_rto_consignment|RTO_RECEIPT|rtoBegun|outbound/rto\b',
    'RMV-UNR-09': r'ObsolescenceReturn|ObsolescenceCandidate|ObsolescenceWindow|wh_obsolescence_return|OBSOLESCENCE_RETURN|TYPE_OBSOLESCENCE|warehouse\.obsolescence_returns|inbound/obsolescence-returns',
    'RMV-UNR-10': r'TradePortal|TradeCustomer|CustomerPersona|wh_trade_portal|permittedCustomers|requireCustomerPermitted|CustomerScope|ForCustomer\b|toCustomerResponses|createTradePortalDraft|outbound/trade-portal|WAREHOUSE_TRADE_PORTAL_USER|tradePortal|CUSTOMER_PATH|exportCustomerDemandOrders|downloadCustomerDocument|isCustomerUnscoped|customerUnscopedAuthorities|customerGrantProviders|CUSTOMER_NOT_PERMITTED|PERSONA_PARAMETERS|warehouse_trade\b',
    'RMV-UNR-11': r'Coexistence|CategoryStockingOwnership|ExternalStockSnapshot|StockingSystem|InventorySeparation|whb_category_stocking_ownership|whb_external_stock_snapshot|wh_rpt_coexistence|is_dual_eligible|isDualEligible|masters/category-ownership|platform/external-snapshots|reports/coexistence',
    'RMV-UNR-12': r'ConsolidatedValuation|wh_rpt_consolidated_valuation|reports/consolidated-valuation',
    'RMV-UNR-13': r'adapter\.dealer|adapter\.services|warehouse-adapter-(dealer|services)|warehouseadapter(dealer|services)|Parts Counter|Workshop Parts|WAREHOUSE_(DEALER|SERVICES)_|whad_|whas_',
}

# A class token has a lower-case letter, so EXIT / LIMIT / ADMIT / IN_TRANSIT / W53_COMMIT never match.
CLASS = re.compile(r'(?<![\w*$])((?:[a-z0-9_]+\.)*[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9()]*(?:Test|IT))(?:\$\w+)?(?:[#.]([a-z]\w*))?\b')


def sources():
    found = {}
    for tree in TREES:
        for base, dirs, files in os.walk(os.path.join(ROOT, tree)):
            dirs[:] = [d for d in dirs if d not in ('node_modules', 'target', '.next')]
            if '/src/test' not in base.replace(os.sep, '/'):
                continue
            for name in files:
                stem, ext = os.path.splitext(name)
                if ext in ('.java', '.ts', '.tsx'):
                    found.setdefault(stem[:-5] if stem.endswith('.test') else stem, os.path.join(base, name))
    return found


def spellings(token):
    simple = token.rsplit('.', 1)[-1]
    m = re.search(r'\(([A-Za-z0-9]+)\)', simple)
    return [simple] if not m else [simple.replace(m.group(0), ''), simple.replace(m.group(0), m.group(1))]


def main():
    files = sources()
    lines = open(DEF, encoding='utf-8').read().split('\n')
    bad = []
    for n, line in enumerate(lines, 1):
        for m in CLASS.finditer(line):
            for simple in spellings(m.group(1)):
                path = files.get(simple)
                if path is None:
                    bad.append(f'{n}: class {simple} not found')
                elif m.group(2) and not re.search(r'\b' + re.escape(m.group(2)) + r'\b', open(path, encoding='utf-8').read()):
                    bad.append(f'{n}: method {simple}#{m.group(2)} not found')
        for gate, pattern in GATES.items():
            if re.search(pattern, line):
                bad.append(f'{n}: {gate} hit')
    print('\n'.join(bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
