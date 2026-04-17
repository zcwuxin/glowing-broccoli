from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from fastapi import APIRouter,Depends,HTTPException,Query
from app.dao import stu_offers_dao
from app.scheme import  stu_offers_request,stu_offers_response
stu_offers_route=APIRouter()
security = HTTPBearer()


###添加学生信息
@stu_offers_route.post("/offers",summary="添加学生就业信息")
async def add_stu_o_info(stu_o_a_info:stu_offers_request.stu_info_front,db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        new_add=stu_offers_dao.add__stu_o_info(
            db=db,
            s_id=stu_o_a_info.s_id,
            o_company=stu_o_a_info.o_company,
            o_salary=stu_o_a_info.o_salary,
            o_open_date=stu_o_a_info.o_open_date,
            o_send_date=stu_o_a_info.o_send_date
            # ** stu_o_a_info.dict()
        )
        return new_add
    except Exception as e:
        return {"message":"添加失败","code":500, "msg":e}


###删除学生信息，根据o_id来删,dao层已经处理异常，这里只需返回就行
@stu_offers_route.delete("/offers/{o_id}",summary="删除学生就业信息")
async def del_stu_o_info(
        del_stu_info:stu_offers_request.stu_info_del,
        db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return stu_offers_dao.del_stu_o_info_api(db,**del_stu_info.dict())#解包操作，直接将del_stu_info参数作为字典传入另一个参数


###修改学生信息,根据o_id来修改字段,dao层已经处理异常，这里只需返回就行
@stu_offers_route.patch("/offers/{o_id}",summary="修改学生就业信息")
async def alter_stu_o_info(
    del_stu_info:stu_offers_request.stu_info_alter,
    db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return stu_offers_dao.stu_o_info_alter(
            db=db,
            o_id=del_stu_info.o_id,
            s_id=del_stu_info.s_id,
            o_company=del_stu_info.o_company,
            o_salary=del_stu_info.o_salary,
            o_open_date=del_stu_info.o_open_date,
            o_send_date=del_stu_info.o_send_date)

###查询学生就业
@stu_offers_route.get("/offers",summary="查询学生就业信息")
async def get_stu_o_id_api(s_id:int=Query(None,description="学生id"),
                       o_company:str=Query(None,description="公司名称"),
                       min_salary: float = Query(None, ge=0, description="最低工资"),
                       max_salary: float = Query(None, ge=0, description="最高工资"),
                       db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)
                       ):
    try:
        res_data=stu_offers_dao.get_stu_o_info(db,s_id, o_company, min_salary, max_salary)
        if res_data and len(res_data)>0:
            return {"message": "查询成功", "code": 200, "data": res_data}
        else:
            return {"message": "报意思啊，查无此信息", "code": 404, "data": None}
    except Exception as e:
        return {"message": f"查询异常: {str(e)}", "code": 500, "data": None}

