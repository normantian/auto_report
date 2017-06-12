SELECT a.uuid as '案件编号', a.title as '标题', ci.company_name as '公司', b.court_time as '开庭时间',l.lawyer_name as '律师姓名',l.law_firm_name as '律所名称',kceo.`name` as '诉讼对方'
FROM
(SELECT * FROM `kv_case_entrust` as a WHERE a.company_id in (2,4,21,29,81,1050,1442,2344,2377)) a
LEFT JOIN
(
	SELECT * 
	FROM `kv_case_court_time` 
	 -- WHERE court_time>curdate()
	WHERE court_time BETWEEN curdate() AND date_add(curdate(), INTERVAL 2 WEEK)
) 
AS b ON a.id = b.target_id -- AND b.target_type='1'
LEFT JOIN 
kv_case_apply as c
ON c.target_id = a.id and c.apply_status='1029000005'
LEFT JOIN 
kv_lawyer_info as l
ON l.id = c.lawyer_id
LEFT JOIN 
kv_company_info as ci
ON ci.id = a.company_id
LEFT JOIN
kv_case_entrust_opponent as kceo
ON a.id = kceo.case_entrust_id
WHERE court_time IS NOT NULL 
ORDER BY b.court_time;