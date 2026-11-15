# 原供应商微观接单与原生供货选择

运行 `& './run.ps1'`。实际 Supplier.consider_supply_order 请求执行原 SUPPLIER-A04 和原容量方法；最终确认复用同一结果。
默认承包商选供应商显式使用原 ContractorAgent.select_supplier，再确认同一提案；启用 --with-contractor 时改用原微观 A05。
两项目从明确的合成合同确认阶段开始：首项目已有签订记录及占用 0.8 的承包商委任，与企业初始占用一致；后续项目由原生命周期在时点 1 签订，时点 2 选择供应商。
所有具体产品、报价、已收订单提议、独立买方预先同意条款、库存、资金、容量、生产率、交期和比较指标均为明确合成来源，不由宏观规范化资源推导。
买方预先条款同意仅为显式初始假设，不是将未来承包商选中结果伪装成已签署回执。
默认供应商 A 配置较早一次实际被选中后拒绝新接单，B 不启用该策略；--with-contractor 的独立窗口关闭该拒单策略。真实本组织反馈经原事件、提案、最终确认和微观结果核对。
原生选供仅代表项目供货安排/就绪，不创建细粒度 SupplyOrder、库存预留、资金支付或第二套正式账本。库存和资金的时点快照是独立假设，不能据选中自动扣减。
部分接受、修订或未知结果保留未决状态，不冒充完整接受或原生规则兜底。真实资料、其他分支及 C3 履约继续接线。
本包显式启用 A03：独立收到的询价、已确认产品提议、每件 80 HKD 工厂成本和 25% 加成均为合成假设。原 A03 实际执行计价及容量方法后，A04 核对全部报价行、付款条款、现有库存/容量与独立提供的 200 HKD 提议一致。私有交接 Evidence 由实际 A03 任务/结果/来源生成；没有正式报价登记回执，也不改写独立条款。
本包显式启用 A02：同一收到的询价、工厂/用途/材料约束及目录属性证据均为合成假设，未声明独立设计检查。原 A02 实际调用兼容性方法；原 A02→A03 交接核对保存结果、完整产品行、原询价、授权和真实结果证据。A03 保留独立提供的产品提议及确认状态，A02 不产生专业批准或正式产品登记。
本包显式启用 A01：生产能力、factory_supply 功能权限、10 production-unit 产能及每容量时点 1 panel 生产率为独立合成来源，与 A03/A04 交付资源池及宏观规范化资源分开。原 A01 实算容量，原 A01→A02 交接核对实际完整响应与独立收到的同一询价。收到询价的 Evidence 只观察本次真实读取的合成输入，不是宏观正式收件回执；A01 不产生订单或资源预留。
本包显式启用 CONTRACTOR-A05，取代原生选供规则；不再使用下述默认原生选供配置。本窗口明确关闭供应商 A 的中选后拒单策略，两供应商均继续接受。承包商初始偏好 A/B，并明确配置较早本机构中选后优先级惩罚 2。实际 A03 报价和 A04 接单支持独立收到的完整条款，经原 A05 验证后返回原生选供；后续 A05 读取本机构真实反馈后选择 B。A05 的主合同采购额度、收货/检验/付款/绑定权限及初始独立供应商签署视图是明确合成输入；初始作者授权不冒充本次 A03 签署。不披露供应商成本、库存、资金或策略；只对照准确报价行和付款规则。宏观选供不产生详细订单、正式供货合同、承诺占用或付款。


以上两时点时序及 200 HKD 报价说明针对默认 supply-first / supply-followup。initial-supply-windows.json 另列的窗口仅为共享宿主预先提供微观资料，不在本子包预置对应项目或合同；具体交期、报价比例及采购限额按各窗口明确输入，供应商初始现金保持 1000 HKD。追加窗口必须由原宏观先产生本轮实际签约事件，后续真实请求才能执行；缺该事件保持未决。

--allow-saved-recovery enables queries of the original in-process completed terminal result; --query-saved-supply-on-error returns it to the still-open native call after technical interruption. No missing-result replay, unstarted stage, engine restart, formal order or payment. Both flags default off.

--with-product-substitution requires --with-quote --with-product and declares an independent initial alternate catalogue code and versioned deviation. Original A02/A03/A04 preserve that deviation. With --with-contractor, original A05 reads independent requirement-level substitution permission; --withhold-contractor-substitution-permission leaves its needs_information result unresolved. Initial commercial assent is separate from this permission; neither is a product approval or delivery receipt.

--continue-unstarted-actions-on-error defaults off. It continues once only when the original worker proves the same registered action has not started preparation, within the still-open original native call. Earlier actions and source producers are not rerun. Started preparation, missing results and changed sources/authority stay unresolved. Independent of saved-result recovery; no engine/process restart.
