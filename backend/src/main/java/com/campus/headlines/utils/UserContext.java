package com.campus.headlines.utils;

public class UserContext {

    public record CurrentUser(Long id, String role, String name, Integer userRole, Long wmUserId) {
    }

    private static final ThreadLocal<CurrentUser> HOLDER = new ThreadLocal<>();

    public static void set(CurrentUser user) {
        HOLDER.set(user);
    }

    public static CurrentUser get() {
        return HOLDER.get();
    }

    /** ap_user.id：点赞、评论、个人资料 */
    public static Long userId() {
        CurrentUser user = HOLDER.get();
        return user == null ? null : user.id();
    }

    /** wm_user.id：素材、文章、审核 */
    public static Long wmUserId() {
        CurrentUser user = HOLDER.get();
        return user == null ? null : user.wmUserId();
    }

    public static Integer userRole() {
        CurrentUser user = HOLDER.get();
        return user == null ? null : user.userRole();
    }

    public static String role() {
        CurrentUser user = HOLDER.get();
        return user == null ? null : user.role();
    }

    public static CurrentUser requireUser() {
        CurrentUser user = HOLDER.get();
        if (user == null) {
            throw new com.campus.headlines.common.BusinessException(401, "请先登录");
        }
        return user;
    }

    public static void clear() {
        HOLDER.remove();
    }
}
