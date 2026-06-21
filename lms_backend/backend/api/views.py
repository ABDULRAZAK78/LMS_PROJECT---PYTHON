from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import jwt
import datetime
from django.conf import settings
import bcrypt
import base64
import uuid


def safe_val(v):
    if isinstance(v, (bytes, bytearray, memoryview)):
        try:
            return v.tobytes().hex() if isinstance(v, memoryview) else v.hex()
        except:
            return None
    return v


def hex_to_binary(hex_str):
    try:
        hex_str = hex_str.replace("-", "")
        return bytes.fromhex(hex_str)
    except:
        return None


# =========================================================
# 🔐 REGISTER
# =========================================================
@api_view(['POST'])
def register_user(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")
        username = request.data.get("username", "")
        mobile_number = request.data.get("mobileNumber", "")
        dob = request.data.get("dob", "")
        gender = request.data.get("gender", "")
        location = request.data.get("location", "")
        profession = request.data.get("profession", "")
        linkedin_url = request.data.get("linkedin_url", "")
        github_url = request.data.get("github_url", "")

        if not email or not password:
            return Response({"success": False, "error": "Email & password required"})

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", [email])
            if cursor.fetchone():
                return Response({"success": False, "error": "User already exists"})

            user_id = uuid.uuid4().bytes

            cursor.execute("""
                INSERT INTO users (id, email, password, role, username, mobile_number,
                                   dob, gender, location, profession, linkedin_url,
                                   github_url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, [
                user_id, email, hashed_password, "USER",
                username or email.split("@")[0],
                mobile_number, dob, gender, location,
                profession, linkedin_url, github_url
            ])

        return Response({"success": True, "message": "User registered successfully"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 🔐 LOGIN
# =========================================================
@api_view(['POST'])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, password, email, role, username
                FROM users
                WHERE email = %s
            """, [email])

            row = cursor.fetchone()

            if not row:
                return Response({"success": False, "error": "User not found"})

            user_id, db_password, email, role, username = row

            if not bcrypt.checkpw(password.encode(), db_password.encode()):
                return Response({"success": False, "error": "Invalid password"})

            payload = {
                "user_id": safe_val(user_id),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                "iat": datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            return Response({
                "success": True,
                "data": {
                    "token": token,
                    "id": safe_val(user_id),
                    "name": username or "",
                    "email": email,
                    "role": role
                }
            })

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 📚 COURSES
# =========================================================
@api_view(['GET'])
def get_courses(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT course_id, course_name, description, instructor, p_link, price, y_link
                FROM course
            """)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = []
        for row in rows:
            item = {}
            for col, val in zip(columns, row):
                item[col] = safe_val(val)
            data.append(item)

        return Response({"success": True, "data": data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['GET'])
def get_course_detail(request, course_id):
    try:
        binary_id = hex_to_binary(course_id)

        if not binary_id:
            return Response({"success": False, "error": "Invalid ID"})

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT course_id, course_name, description, instructor, p_link, price, y_link
                FROM course
                WHERE course_id = %s
            """, [binary_id])

            row = cursor.fetchone()

            if not row:
                return Response({"success": False, "error": "Not found"})

            columns = [col[0] for col in cursor.description]

        data = {}
        for col, val in zip(columns, row):
            data[col] = safe_val(val)

        return Response({"success": True, "data": data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 🎓 ENROLL — ✅ FIXED with uuid id
# =========================================================
@api_view(['POST'])
def enroll_user(request):
    try:
        user_id = request.data.get("user_id")
        course_id = request.data.get("course_id")

        user_bin = hex_to_binary(user_id)
        course_bin = hex_to_binary(course_id)

        if not user_bin or not course_bin:
            return Response({"success": False, "error": "Invalid IDs"})

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM learning
                WHERE user_id = %s AND course_id = %s
            """, [user_bin, course_bin])

            if cursor.fetchone():
                return Response({"success": True, "message": "Already enrolled"})

            cursor.execute("""
                INSERT INTO learning (id, user_id, course_id)
                VALUES (%s, %s, %s)
            """, [uuid.uuid4().bytes, user_bin, course_bin])

        return Response({"success": True, "message": "Enrolled successfully"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['GET'])
def get_user_enrollments(request, user_id):
    try:
        user_bin = hex_to_binary(user_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.course_id, c.course_name, c.description, c.instructor, c.p_link, c.price, c.y_link
                FROM learning l
                JOIN course c ON l.course_id = c.course_id
                WHERE l.user_id = %s
            """, [user_bin])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = []
        for row in rows:
            item = {}
            for col, val in zip(columns, row):
                item[col] = safe_val(val)
            data.append(item)

        return Response({"success": True, "data": data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['GET'])
def check_enrollment(request, user_id, course_id):
    try:
        user_bin = hex_to_binary(user_id)
        course_bin = hex_to_binary(course_id)

        if not user_bin or not course_bin:
            return Response({"success": False, "error": "Invalid IDs"})

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM learning
                WHERE user_id = %s AND course_id = %s
            """, [user_bin, course_bin])

            exists = cursor.fetchone() is not None

        return Response({"success": True, "enrolled": exists})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 👤 USER PROFILE
# =========================================================
@api_view(['GET'])
def get_user_details(request, user_id):
    try:
        user_bin = hex_to_binary(user_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, email, role, username, mobile_number, gender, dob,
                       profession, location, linkedin_url, github_url
                FROM users
                WHERE id = %s
            """, [user_bin])

            row = cursor.fetchone()

            if not row:
                return Response({"success": False, "error": "User not found"})

            columns = [col[0] for col in cursor.description]
            user_data = {}
            for col, val in zip(columns, row):
                user_data[col] = safe_val(val)

            cursor.execute("SELECT COUNT(*) FROM learning WHERE user_id = %s", [user_bin])
            count_row = cursor.fetchone()
            learning_count = count_row[0] if count_row else 0

        user_data["learningCourses"] = [None] * learning_count

        return Response({"success": True, "data": user_data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['PUT'])
def update_user(request, user_id):
    try:
        user_bin = hex_to_binary(user_id)
        data = request.data

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE users SET
                    username = %s,
                    mobile_number = %s,
                    gender = %s,
                    dob = %s,
                    profession = %s,
                    location = %s,
                    linkedin_url = %s,
                    github_url = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, [
                data.get("username"),
                data.get("mobileNumber"),
                data.get("gender"),
                data.get("dob"),
                data.get("profession"),
                data.get("location"),
                data.get("linkedin_url"),
                data.get("github_url"),
                user_bin
            ])

        return Response({"success": True, "message": "Profile updated"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['GET'])
def get_profile_image(request, user_id):
    try:
        user_bin = hex_to_binary(user_id)

        with connection.cursor() as cursor:
            cursor.execute("SELECT profile_image FROM users WHERE id = %s", [user_bin])
            row = cursor.fetchone()

        if not row or not row[0]:
            return Response({"success": False, "error": "No image found"}, status=404)

        image_data = row[0]
        if isinstance(image_data, memoryview):
            image_data = bytes(image_data)

        encoded = base64.b64encode(image_data).decode("utf-8")
        return Response({
            "success": True,
            "image": f"data:image/jpeg;base64,{encoded}"
        })

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['POST'])
def upload_profile_image(request, user_id):
    try:
        user_bin = hex_to_binary(user_id)
        file = request.FILES.get("file")

        if not file:
            return Response({"success": False, "error": "No file provided"})

        image_bytes = file.read()

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE users SET profile_image = %s WHERE id = %s
            """, [image_bytes, user_bin])

        return Response({"success": True, "message": "Image uploaded"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 📊 PROGRESS
# =========================================================
@api_view(['GET'])
def get_progress(request, user_id, course_id):
    try:
        user_bin = hex_to_binary(user_id)
        course_bin = hex_to_binary(course_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT played_time, duration FROM progress
                WHERE user_id = %s AND course_id = %s
            """, [user_bin, course_bin])
            row = cursor.fetchone()

        if row and row[1] and row[1] > 0:
            percent = round((row[0] / row[1]) * 100)
        else:
            percent = 0

        return Response({"success": True, "progress": percent})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['POST'])
def update_progress(request, user_id, course_id):
    try:
        user_bin = hex_to_binary(user_id)
        course_bin = hex_to_binary(course_id)
        played_time = request.data.get("played_time", 0)
        duration = request.data.get("duration", 0)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM progress
                WHERE user_id = %s AND course_id = %s
            """, [user_bin, course_bin])
            exists = cursor.fetchone()

            if exists:
                cursor.execute("""
                    UPDATE progress SET played_time = %s, duration = %s
                    WHERE user_id = %s AND course_id = %s
                """, [played_time, duration, user_bin, course_bin])
            else:
                cursor.execute("""
                    INSERT INTO progress (id, played_time, duration, user_id, course_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, [uuid.uuid4().bytes, played_time, duration, user_bin, course_bin])

        return Response({"success": True, "message": "Progress updated"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 💬 FEEDBACK
# =========================================================
@api_view(['GET'])
def get_feedbacks(request, course_id):
    try:
        course_bin = hex_to_binary(course_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, comment, course_id FROM feedback
                WHERE course_id = %s
            """, [course_bin])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = []
        for row in rows:
            item = {}
            for col, val in zip(columns, row):
                item[col] = safe_val(val)
            data.append(item)

        return Response({"success": True, "data": data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['POST'])
def post_feedback(request):
    try:
        course_id = request.data.get("course_id")
        comment = request.data.get("message") or request.data.get("comment")
        course_bin = hex_to_binary(course_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO feedback (id, comment, course_id)
                VALUES (%s, %s, %s)
            """, [uuid.uuid4().bytes, comment, course_bin])

        return Response({"success": True, "message": "Feedback posted"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 🗣️ DISCUSSION
# =========================================================
@api_view(['GET'])
def get_discussions(request, course_id):
    try:
        course_bin = hex_to_binary(course_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, content, time, user_name, course_id FROM discussion
                WHERE course_id = %s
                ORDER BY time DESC
            """, [course_bin])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = []
        for row in rows:
            item = {}
            for col, val in zip(columns, row):
                item[col] = safe_val(val)
            data.append(item)

        return Response({"success": True, "data": data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['POST'])
def post_discussion(request):
    try:
        course_id = request.data.get("course_id")
        content = request.data.get("message") or request.data.get("content")
        user_name = request.data.get("user_name", "Anonymous")
        course_bin = hex_to_binary(course_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO discussion (id, content, time, user_name, course_id)
                VALUES (%s, %s, NOW(), %s, %s)
            """, [uuid.uuid4().bytes, content, user_name, course_bin])

        return Response({"success": True, "message": "Message posted"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


# =========================================================
# 🏆 ASSESSMENT & QUESTIONS
# =========================================================
@api_view(['GET'])
def get_performance(request, user_id):
    try:
        user_bin = hex_to_binary(user_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.id, a.marks, a.course_id, c.course_name
                FROM assessment a
                JOIN course c ON a.course_id = c.course_id
                WHERE a.user_id = %s
            """, [user_bin])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = []
        for row in rows:
            item = {}
            for col, val in zip(columns, row):
                item[col] = safe_val(val)
            data.append(item)

        return Response({"success": True, "data": data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['GET'])
def get_assessment(request, course_id):
    try:
        course_bin = hex_to_binary(course_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, question, option1, option2, option3, option4, answer
                FROM questions
                WHERE course_id = %s
            """, [course_bin])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = []
        for row in rows:
            item = {}
            for col, val in zip(columns, row):
                item[col] = safe_val(val)
            data.append(item)

        return Response({"success": True, "data": data})

    except Exception as e:
        return Response({"success": False, "error": str(e)})


@api_view(['POST'])
def submit_assessment(request):
    try:
        user_id = request.data.get("user_id")
        course_id = request.data.get("course_id")
        marks = request.data.get("marks") or request.data.get("score", 0)

        user_bin = hex_to_binary(user_id)
        course_bin = hex_to_binary(course_id)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO assessment (id, marks, user_id, course_id)
                VALUES (%s, %s, %s, %s)
            """, [uuid.uuid4().bytes, marks, user_bin, course_bin])

        return Response({"success": True, "message": "Assessment submitted"})

    except Exception as e:
        return Response({"success": False, "error": str(e)})