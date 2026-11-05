package com.campus.headlines.interceptor;

import com.campus.headlines.common.Result;
import com.campus.headlines.utils.JwtUtils;
import com.campus.headlines.utils.UserContext;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.nio.charset.StandardCharsets;

/**
 * Spring MVC 拦截器：解析 JWT，写入用户上下文，并按角色拦截接口。
 */
@Component
@RequiredArgsConstructor
public class AuthInterceptor implements HandlerInterceptor {

    private final JwtUtils jwtUtils;
    private final ObjectMapper objectMapper;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }
        String uri = request.getRequestURI();
        String token = resolveToken(request);
        if (token != null) {
            try {
                Claims claims = jwtUtils.parse(token);
                Long id = Long.valueOf(claims.getSubject());
                String role = claims.get("role", String.class);
                String name = claims.get("name", String.class);
                Integer userRole = claims.get("userRole", Integer.class);
                Long wmUserId = claims.get("wmUserId", Long.class);
                UserContext.set(new UserContext.CurrentUser(id, role, name, userRole, wmUserId));
            } catch (Exception ignored) {
                UserContext.clear();
            }
        }

        boolean needMedia = uri.startsWith("/api/media/") && !uri.equals("/api/media/auth/login");
        boolean postComment = "POST".equalsIgnoreCase(request.getMethod())
                && uri.matches("^/api/news/\\d+/(like|comments)$");
        boolean needUser = uri.equals("/api/auth/me")
                || uri.equals("/api/auth/logout")
                || uri.equals("/api/auth/profile")
                || uri.equals("/api/auth/avatar")
                || postComment;

        if (needMedia && (UserContext.userRole() == null || UserContext.userRole() == 0)) {
            return reject(response, "请先登录作者或审核员账号");
        }
        if (needUser && UserContext.get() == null) {
            return reject(response, "请先登录后再操作");
        }
        return true;
    }

    private String resolveToken(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        if (header == null || header.isEmpty()) {
            return null;
        }
        return header.startsWith("Bearer ") ? header.substring(7).trim() : header.trim();
    }

    private boolean reject(HttpServletResponse response, String message) throws Exception {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.setContentType("application/json;charset=UTF-8");
        objectMapper.writeValue(response.getWriter(), Result.fail(401, message));
        return false;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        UserContext.clear();
    }
}
