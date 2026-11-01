import {
  Building2,
  CloudSun,
  HandCoins,
  Sprout,
  Store,
  Users,
} from 'lucide-react'

export const evidenceSources = [
  {
    id: 'chama',
    title: 'Chama records',
    subtitle: 'Contributions and savings',
    icon: Users,
    contribution:
      'Dated contribution and savings records could show a pattern of financial participation over time. A chama is a community savings group; the underlying records matter more than membership alone.',
    connection:
      'Applicant → membership → savings group → contribution entries. Each entry needs a source, date and confirmed applicant reference.',
    limit:
      'Membership, social connections or popularity do not establish ability to repay. Missing entries need review, rather than an automatic negative judgment.',
    availability:
      'The development graph contains fictional savings groups, memberships and contribution entries. No real chama partner feed is connected.',
  },
  {
    id: 'sacco',
    title: 'SACCO & lender records',
    subtitle: 'Loans and repayments',
    icon: Building2,
    contribution:
      'A SACCO—a savings and credit cooperative—or another lender could provide documented loans, scheduled installments and repayments, allowing an officer to inspect obligations and payment history.',
    connection:
      'Applicant → lender → loan → installment and repayment records. Confirmed references keep one person’s history separate from another’s.',
    limit:
      'Past repayments do not guarantee future repayment. Current obligations and the completeness of the supplied history still need checking.',
    availability:
      'Scoped fictional lender, loan and repayment histories are available in the prototype. A direct SACCO account integration is not connected.',
  },
  {
    id: 'cooperative',
    title: 'Cooperative activity',
    subtitle: 'Deliveries and receipts',
    icon: Sprout,
    contribution:
      'Recorded produce deliveries and sale receipts could help explain seasonal earning activity that a conventional monthly payslip would not capture.',
    connection:
      'Applicant → cooperative membership → delivery or sale entry → counterparty. Dates and source records let an officer follow the activity.',
    limit:
      'A delivery does not establish profit or disposable income. Costs, household needs and unpaid obligations may be missing.',
    availability:
      'Cooperative memberships, delivery entries and farm-sale receipts are authored synthetic replay. They are not verified customer earnings.',
  },
  {
    id: 'business',
    title: 'Business cash flow',
    subtitle: 'Sales and transactions',
    icon: Store,
    contribution:
      'For a small business without conventional collateral, permissioned sales, supplier and transaction records could help a lender understand trading activity and the timing of cash flow.',
    connection:
      'Applicant → business activity → dated transaction → counterparty. A future partner connection would need permission and reliable identity matching.',
    limit:
      'Turnover is not profit, and repeated transactions are not a credit score. Expenses, existing debt and authentic source records are essential.',
    availability:
      'Today’s workflow focuses on agricultural input finance and fictional farm-sale histories. General small-business account integrations are a planned extension.',
  },
  {
    id: 'context',
    title: 'Farm & climate context',
    subtitle: 'Seasons and reference weather',
    icon: CloudSun,
    contribution:
      'Crop, season and weather context can help an officer interpret agricultural activity in context, rather than reading a seasonal business as a uniform monthly income stream.',
    connection:
      'Applicant → farm → crop season or assigned reference region → attributed weather records. Financial history and environmental context remain distinct.',
    limit:
      'Regional weather is not a verified farm measurement or a prediction of default. The prototype’s region assignments are fictional.',
    availability:
      'Authored farm and crop records are linked to separately attributed public weather at reference points. No verified farm-location or calibrated climate-risk score is claimed.',
  },
  {
    id: 'execution',
    title: 'Input finance records',
    subtitle: 'Decisions, payment and collection',
    icon: HandCoins,
    contribution:
      'After a lender authorizes credit, the platform connects an input request, supplier invoice, verified payment and recorded collection. These remain separate, inspectable events.',
    connection:
      'Lender decision → authorized allocation → input order → supplier invoice → payment evidence → collection record, when one is actually recorded.',
    limit:
      'An AI summary cannot approve a loan. An invoice marked paid is insufficient on its own, and a verified payment does not prove physical collection.',
    availability:
      'The signed lender handoff and transaction controls are implemented. A separate USD 18 sandbox payment and genuine callback were verified; its collection was not recorded.',
  },
] as const
