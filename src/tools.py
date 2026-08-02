"""
Tool registry for the Career Orientation ReAct Agent.

All tools are deterministic and offline-friendly so the lab can run without
external APIs. Business errors are returned as strings instead of exceptions.
"""


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def get_career_info(career_name: str) -> str:
    """
    Look up basic information about a career.

    Args:
        career_name: Career name, for example "Data Analyst" or "UI/UX Designer".

    Returns:
        A short description of duties, useful skills, and a junior entry path.
        Returns an error string when the career is unsupported.
    """
    career = _normalize(career_name)
    career_db = {
        "data analyst": (
            "Data Analyst: thu thap, lam sach, phan tich du lieu va tao bao cao. "
            "Ky nang can co: Excel, SQL, Python co ban, thong ke, truc quan hoa du lieu. "
            "Vi tri dau vao: Data Analyst Intern, BI Intern, Reporting Analyst."
        ),
        "ui/ux designer": (
            "UI/UX Designer: nghien cuu nguoi dung, ve wireframe, thiet ke giao dien va kiem thu trai nghiem. "
            "Ky nang can co: Figma, tu duy san pham, visual design, user research, prototyping. "
            "Vi tri dau vao: UI Designer Intern, UX Research Intern, Product Design Intern."
        ),
        "backend developer": (
            "Backend Developer: xay dung API, xu ly database, logic nghiep vu va he thong may chu. "
            "Ky nang can co: Python/Java/Node.js, SQL, API, Git, debugging. "
            "Vi tri dau vao: Backend Intern, Software Engineer Intern."
        ),
        "product manager": (
            "Product Manager: xac dinh bai toan nguoi dung, uu tien tinh nang, lam viec voi engineering/design/business. "
            "Ky nang can co: giao tiep, phan tich, product thinking, viet requirement, do luong metric. "
            "Vi tri dau vao: Product Intern, Business Analyst, Associate Product Manager."
        ),
    }

    for key, value in career_db.items():
        if key in career:
            return value
    return f"LOI: Chua co du lieu nghe nghiep cho '{career_name}'."


def assess_career_fit(profile: str) -> str:
    """
    Assess suitable careers from a student's interests and skills.

    Args:
        profile: Free-text profile containing interests, current skills, major,
            and constraints.

    Returns:
        Ranked career suggestions with reasons and confidence level.
        Returns a safe warning string when the profile is too vague.
    """
    text = _normalize(profile)
    if not text:
        return "LOI: Ho so trong. Can them thong tin ve so thich, ky nang hoac nganh hoc."

    if "khong co ky nang" in text and "khong muon hoc" in text:
        return (
            "CANH BAO: Ho so hien tai chua du co so de cam ket mot muc tieu nghe nghiep lon. "
            "Nguoi dung can chon it nhat mot ky nang nen tang va mot thoi gian hoc tap thuc te."
        )

    if ("toan" in text or "so lieu" in text or "python" in text) and "phan tich" in text:
        return (
            "Phu hop nhat: Data Analyst (do phu hop 85%). "
            "Ly do: nguoi dung thich toan, co Python co ban va thich phan tich so lieu. "
            "Lua chon phu: Business Analyst (70%) neu muon lam gan voi nghiep vu."
        )

    if "thiet ke" in text or "giao dien" in text or "figma" in text:
        return (
            "Phu hop nhat: UI/UX Designer (do phu hop 80%). "
            "Ly do: nguoi dung hoc CNTT, thich thiet ke giao dien va khong muon tap trung qua nhieu vao toan nang. "
            "Lua chon phu: Frontend Developer (65%) neu san sang hoc JavaScript va HTML/CSS sau hon."
        )

    if "lap trinh" in text or "backend" in text or "api" in text:
        return (
            "Phu hop nhat: Backend Developer (do phu hop 78%). "
            "Ly do: ho so co dau hieu phu hop voi lap trinh logic, API va xu ly du lieu."
        )

    return (
        "Chua du thong tin de xep hang nghe nghiep chinh xac. "
        "Can bo sung: mon hoc yeu thich, ky nang hien co, dieu khong thich va muc tieu 6-12 thang."
    )


def suggest_learning_path(career_name: str) -> str:
    """
    Suggest a learning path for a target career.

    Args:
        career_name: Target career name.

    Returns:
        A practical 3-step learning path for the career.
        Returns an error string when the career is unsupported.
    """
    career = _normalize(career_name)
    if "data analyst" in career:
        return (
            "Lo trinh Data Analyst: "
            "1) Hoc Excel/Google Sheets va thong ke co ban; "
            "2) Hoc SQL va Python pandas; "
            "3) Lam 2 portfolio project ve dashboard va phan tich du lieu thuc te."
        )
    if "ui/ux" in career or "designer" in career:
        return (
            "Lo trinh UI/UX Designer: "
            "1) Hoc Figma, layout, typography va design system; "
            "2) Lam user research, wireframe, prototype; "
            "3) Tao 2 case study: app sinh vien va landing page san pham."
        )
    if "backend" in career:
        return (
            "Lo trinh Backend Developer: "
            "1) Hoc Python/JavaScript backend co ban; "
            "2) Hoc REST API, SQL, authentication va Git; "
            "3) Lam project API co database va deploy ban demo."
        )
    return f"LOI: Chua co lo trinh hoc cho '{career_name}'."


def check_goal_realism(goal: str) -> str:
    """
    Check whether a career goal is realistic and safe to advise on.

    Args:
        goal: User's stated career goal or demand.

    Returns:
        A guardrail message when the goal is unrealistic, otherwise a practical note.
    """
    text = _normalize(goal)
    if "dam bao" in text or "ceo" in text and "1 thang" in text:
        return (
            "GUARDRAIL: Khong the dam bao thanh CEO trong 1 thang. "
            "Tu van an toan nen tap trung vao muc tieu nho, do duoc: chon 1 ky nang, hoc 4-8 tuan, "
            "lam 1 project va xin feedback."
        )
    return "Muc tieu co the thao luan tiep neu co moc thoi gian, ky nang hien tai va tieu chi do luong ro rang."


AVAILABLE_TOOLS = {
    "get_career_info": get_career_info,
    "assess_career_fit": assess_career_fit,
    "suggest_learning_path": suggest_learning_path,
    "check_goal_realism": check_goal_realism,
}
