package com.gigigenie.domain.favorite.repository;

import com.gigigenie.domain.favorite.entity.Favorite;
import com.gigigenie.domain.member.entity.Member;
import com.gigigenie.domain.product.entity.Product;
import jakarta.validation.constraints.NotNull;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface FavoriteRepository extends JpaRepository<Favorite, Integer> {
    List<Favorite> findByMember(@NotNull Member member);

    void deleteByProductAndMember(@NotNull Product product, @NotNull Member member);
}
