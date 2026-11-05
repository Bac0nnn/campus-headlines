package com.campus.headlines.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;

@Component
public class JwtUtils {

    @Value("${campus.jwt.secret}")
    private String secret;

    @Value("${campus.jwt.expire-days:7}")
    private int expireDays;

    private Key key() {
        return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    /**
     * 统一签发：subject 为 ap_user.id，附带 userRole（0普通/1作者/2审核员）与 wmUserId。
     */
    public String createToken(Long apUserId, String role, String name, Integer userRole, Long wmUserId) {
        Date now = new Date();
        Date expire = new Date(now.getTime() + expireDays * 24L * 60 * 60 * 1000);
        return Jwts.builder()
                .setSubject(String.valueOf(apUserId))
                .claim("role", role)
                .claim("name", name)
                .claim("userRole", userRole)
                .claim("wmUserId", wmUserId)
                .setIssuedAt(now)
                .setExpiration(expire)
                .signWith(key(), SignatureAlgorithm.HS256)
                .compact();
    }

    public Claims parse(String token) {
        return Jwts.parserBuilder().setSigningKey(key()).build().parseClaimsJws(token).getBody();
    }
}
