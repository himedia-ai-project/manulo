package com.gigigenie.domain.member.repository;

import com.gigigenie.domain.member.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface MemberRepository extends JpaRepository<Member, Integer>{
    @Query("select u from Member u where u.email = :email")
    Optional<Member> findByEmail(@Param("email") String email);

}
